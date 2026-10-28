import pymupdf
from PIL import Image

from src.schemas.box import Bbox
from src.schemas.template import LLMFormField
from services.base.worker import BaseWorker
from src.schemas.output import Page
from io import BytesIO
import time


from src.logger import logger
from src.schemas.task import (
    TaskModel,
    TaskStatus,
    TaskUpdateForm,
    TaskOperation,
    task_table,
)


# TODO: need to be refactored to simplify the worker and use the new BaseWorker
class PDFFormsExtractorWorker(BaseWorker):
    def __init__(
        self,
        name,
        file_connector,
        models=[],
        batch_size=2,
        worker_weight=1,
        cache=None,
    ):
        super().__init__(
            name,
            file_connector,
            models=models,
            batch_size=batch_size,
            worker_weight=worker_weight,
            cache=cache,
        )
        self._cached_doc: pymupdf.Document = None

    def _get_cached_document(self, task: TaskModel) -> pymupdf.Document:
        # Always open a fresh document — no cross-task caching to avoid stale state
        self._clear_cached_document()
        tmp_filename = self.get_content_file(task=task)
        self._cached_doc = pymupdf.open(tmp_filename)
        return self._cached_doc

    def _clear_cached_document(self):
        """Ferme et libère le document courant"""
        if self._cached_doc is not None:
            self._cached_doc.close()
            self._cached_doc = None

    def is_applicable(self, task: TaskModel) -> bool:
        if task.input.content_type != "application/pdf":
            return False
        t = time.time()
        doc = self._get_cached_document(task)

        logger.debug(
            f"Time to open PDF {task.input.raw_filename} for task {task.id}: {time.time() - t:.2f}s",
        )

        is_form = doc.is_form_pdf

        # Si ce n'est pas un formulaire PDF, nettoyer le cache immédiatement
        if not is_form:
            self._clear_cached_document()

        return is_form

    def predict_on_pages(self, task: TaskModel, pages: list[Image.Image]) -> TaskModel:
        extra_log = {
            "task_id": task.id,
            "user_id": task.user_id,
            "worker_name": self.name,
        }
        if task.input.content_type != "application/pdf":
            logger.error(
                f"Invalid content type {task.input.content_type} for task {task.id}. Expected application/pdf.",
                extra=extra_log,
            )
            return task
        t = time.time()
        doc: pymupdf.Document = self._get_cached_document(task)
        logger.debug(
            f"Time to open PDF {task.input.raw_filename} for task {task.id}: {time.time() - t:.2f}s",
            extra=extra_log,
        )
        if not doc.is_form_pdf:
            return task

        task = self.set_output(task=task, total_pages=len(pages))
        filename = task.input.raw_filename
        client_s3 = self.file_connector.client
        task.output.pages = [Page(page=i) for i in range(len(pages))]
        logger.debug(
            f"[worker {self.name}][Size input images {len(pages)}][Size empty pages {len(task.output.pages)}]",
            extra=extra_log,
        )

        form_bboxs, forms_entries = self.process(task=task)

        for bbox, form_entry, page in zip(
            form_bboxs,
            forms_entries,
            task.output.pages,
        ):
            page.boxes = bbox
            logger.debug(
                f"[worker {self.name}][task-id {task.id}][page {page.page}][boxes {len(bbox)}][{len(form_entry)}]",
                extra=extra_log,
            )
            page.form_entries = form_entry
            page.page_url = None

        task.output.text = ""
        for i in range(0, len(pages), self.batch_size):
            t_predict = time.time()
            batch = pages[i : i + self.batch_size]
            logger.debug(
                f"{filename} for task {task.id}, batch [{i}:{i + self.batch_size}][total: {len(pages)}]",
                extra=extra_log,
            )
            partial_result = task.output.pages[i : i + self.batch_size]
            for model in self.models:
                logger.debug(
                    f"[worker {self.name}][task-id {task.id}][model {model.__class__.__name__}][batch {i}:{i + self.batch_size}][size result : {len(partial_result)}]",
                    extra=extra_log,
                )
                t = time.time()
                partial_result: list[Page] = model.batch_predict(images=batch, pages=partial_result)
                logger.debug(
                    f"[worker {self.name}][task-id {task.id}][model{model.__class__.__name__}][process time {time.time() - t:.2f}]",
                    extra=extra_log,
                )

            for j, image in enumerate(batch):
                buffer = BytesIO()
                image.save(buffer, format="JPEG")
                buffer.seek(0)
                key = f"{task.user_id}/{task.id}/images/page_{i + j}.jpg"
                client_s3.upload_fileobj(buffer, self.file_connector.bucket_name, key)
                logger.debug(
                    f"[worker {self.name}]Uploaded page {i + j} to {key}",
                    extra=extra_log,
                )
                signed_url = client_s3.generate_presigned_url(
                    ClientMethod="get_object",
                    Params={"Bucket": self.file_connector.bucket_name, "Key": key},
                    ExpiresIn=3600,  # 1h
                )
                partial_result[j].page_url = signed_url

            task.output.pages[i : i + self.batch_size] = partial_result

            page_range = f"{i + 1}" if len(batch) == 1 else f"{i + 1}-{i + self.batch_size}"
            logger.debug(
                f"{filename} time to process page {page_range} - {time.time() - t_predict:.2f}s",
                extra=extra_log,
            )

            percentage = (i + len(batch)) / task.output.total_pages
            logger.debug(
                f"[worker {self.name}][Current percentage {100 * percentage:.2f}%]",
                extra=extra_log,
            )
            task.output.set_text()
            task = task_table.update_task(
                task_id=task.id,
                form_data=TaskUpdateForm(
                    status=TaskStatus.IN_PROGRESS.value,
                    percentage=percentage * self.worker_weight,
                    output=task.output,
                    extras=task.extras,
                ),
            )
            logger.debug(
                task.extras,
                extra=extra_log,
            )

        # Nettoyer le cache du document après traitement
        self._clear_cached_document()
        return task

    def process(self, task: TaskModel) -> tuple[list[list[Bbox]], list[list[LLMFormField]]]:
        t = time.time()
        doc: pymupdf.Document = self._get_cached_document(task)
        logger.debug(
            f"[worker {self.name}]Time to open PDF {task.input.raw_filename} for task {task.id}: {time.time() - t:.2f}s",
            extra={"task_id": task.id, "user_id": task.user_id},
        )

        # dpi = 150
        # scale = dpi / 72
        forms_bboxes: list[list[Bbox]] = []
        forms_entries: list[list[LLMFormField]] = []
        t = time.time()

        # Parcours explicite par numéro de page pour garantir l'ordre correct
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_forms: list[LLMFormField] = []
            page_bboxes: list[Bbox] = []
            # pix = page.get_pixmap(dpi=dpi)
            # img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")

            logger.debug(
                f"[worker {self.name}]Processing page {page_num + 1}/{len(doc)} for task {task.id}",
                extra={"task_id": task.id, "user_id": task.user_id},
            )

            for widget in page.widgets():
                name = widget.field_name
                value = widget.field_value

                page_forms.append(
                    LLMFormField(
                        name=name,
                        value=value,
                        type=widget.field_type_string,
                        filled=True,
                    )
                )
                # rect = widget.rect
                # x0, y0 = rect.x0 * scale / img.width, rect.y0 * scale / img.height
                # x1, y1 = rect.x1 * scale / img.width, rect.y1 * scale / img.height

                # page_bboxes.append(
                #     Bbox(
                #         x=x0,
                #         y=y0,
                #         width=x1 - x0,
                #         height=y1 - y0,
                #         confidence=1.0,
                #         text=f"{name} = {value}",
                #     )
                # )
                # TODO: use that if you need real bounding boxes and form entries
            page_width = page.rect.width
            page_height = page.rect.height

            # Get text with positions using dict format
            text_dict = page.get_text("dict")

            for block in text_dict["blocks"]:
                if "lines" in block:  # Text block
                    for line in block["lines"]:
                        for span in line["spans"]:
                            if span["text"].strip():  # Only non-empty text
                                # Normalize coordinates to 0-1 range
                                bbox = Bbox(
                                    text=span["text"],
                                    x=span["bbox"][0] / page_width,  # x0 normalized
                                    y=span["bbox"][1] / page_height,  # y0 normalized
                                    width=(span["bbox"][2] - span["bbox"][0]) / page_width,  # width normalized
                                    height=(span["bbox"][3] - span["bbox"][1]) / page_height,  # height normalized
                                    confidence=1.0,
                                )
                                page_bboxes.append(bbox)
            # TODO: merge overlapping boxes with form entries
            forms_bboxes.append(page_bboxes)
            forms_entries.append(page_forms)
        logger.debug(
            f"[worker {self.name}]Time to process PDF {task.input.raw_filename} for task {task.id}: {time.time() - t:.2f}s",
            extra={"task_id": task.id, "user_id": task.user_id},
        )
        # Nettoyer le cache du document après traitement
        self._clear_cached_document()
        return forms_bboxes, forms_entries


class DefaultPdfExtractor(PDFFormsExtractorWorker):
    def __init__(self, name, file_connector, models=[], batch_size=2, worker_weight=1, cache=None):
        super().__init__(name, file_connector, models, batch_size, worker_weight, cache)

    def is_applicable(self, task: TaskModel) -> bool:
        if task.type == TaskOperation.DEFAULT.value:
            return super().is_applicable(task)
        return False
