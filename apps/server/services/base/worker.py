import time
from typing import List, Optional
from abc import ABC, abstractmethod

from PIL import Image

from services.base.model import BaseModelPrediction
from services.base.cache import BaseCache
from services.utils.lazy_pdf import LazyPdfImageList
from services.utils.lazy_email import LazyEmailList, ZIP_CONTENT_TYPES
from services.utils.lazy_zip import LazyZipList
from business.liteparse.models.liteparse_model import parsed_page_to_schema
from src import __name__, __version__
from src.connector.s3_connector import S3Connector
from src.logger import logger
from src.schemas.output import OCRResult, Page
from src.schemas.task import (
    TaskModel,
    TaskStatus,
    TaskUpdateForm,
    TaskOperation,
    task_table,
)
from src.utils.file import hash_file
from io import BytesIO


EMAIL_CONTENT_TYPES = ("message/rfc822",)


class EmptyContentException(Exception): ...


class FileNotSupported(Exception): ...


class BaseWorker(ABC):
    def __init__(
        self,
        name: str,
        file_connector: S3Connector,
        models: List[BaseModelPrediction],
        batch_size: int = 2,
        worker_weight: int | float = 1,
        cache: Optional[BaseCache] = None,
    ):
        self.name = name
        self.file_connector = file_connector
        self.models = models
        self.worker_weight = worker_weight
        self.batch_size = batch_size
        self.cache = cache

    @abstractmethod
    def is_applicable(self, task: TaskModel) -> bool: ...

    def set_extras(self, task: TaskModel) -> TaskModel:
        task.extras = task.extras if task.extras is not None else {}
        return task

    def get_content_file(self, task: TaskModel) -> str:
        task = self.set_output(task=task)
        try:
            logger.info(f"{task.id} load file ")
            if task.input:
                content = self.file_connector.download_by_s3_key(s3_key=task.input.storage_file_path)
                logger.info(f"{task.id} loaded")
            else:
                content = None
                logger.warning(f"{task.id} no input found")
                raise FileNotFoundError(f"No input found for task : {task.id}")
        except FileNotFoundError as e:
            logger.error(str(e))
            raise FileNotFoundError(str(e))

        except Exception as e:
            task.extras["error"] = str(e)
            task = task_table.update_task(
                task_id=task.id,
                form_data=TaskUpdateForm(status=TaskStatus.FAILED.value, percentage=0, extras=task.extras),
            )
            logger.error(str(e))
            raise

        # if content is None:
        #     task.extras["error"] = f"No content found for task : {task.id}"
        #     task = task_table.update_task(
        #         task_id=task.id,
        #         form_data=TaskUpdateForm(
        #             status=TaskStatus.FAILED.value, percentage=0, extras=task.extras
        #         ),
        #     )
        #     logger.error(f"No content found for task : {task.id}")
        #     raise EmptyContentException(f"No content found for task : {task.id}")
        return content

    def transform_content(self, task: TaskModel, content: bytes) -> List[Image.Image | bytes]:
        task = self.set_output(task=task)

        content_type: str = task.input.content_type
        logger.debug(f"content-type : {content_type}")
        filename = task.input.raw_filename

        if content_type.startswith("image/"):
            pages = [Image.open(content).convert("RGB")]

        elif content_type == "application/pdf":
            t_convert = time.time()
            logger.debug(f"{task.id} - {filename} convert to image")
            logger.info(79 * "*")

            pages = LazyPdfImageList(content)
            t_convert = time.time() - t_convert
            logger.debug(f"{task.id} - {filename} convert to image nb pages {len(pages)} into {t_convert}")

        elif content_type in EMAIL_CONTENT_TYPES:
            t_convert = time.time()
            logger.debug(f"{task.id} - {filename} convert email to image")
            pages = LazyEmailList(content)
            t_convert = time.time() - t_convert
            logger.debug(f"{task.id} - {filename} convert to image nb pages {len(pages)} into {t_convert}")

        elif content_type in ZIP_CONTENT_TYPES:
            t_convert = time.time()
            logger.debug(f"{task.id} - {filename} convert archive to image")
            pages = LazyZipList(content)
            t_convert = time.time() - t_convert
            logger.debug(f"{task.id} - {filename} convert to image nb pages {len(pages)} into {t_convert}")

        else:
            logger.error(f"[worker {self.name}] Unsupported file type {task.extras}")
            task.extras["error"] = f"Unsupported file type {task.extras}"
            task = task_table.update_task(
                task_id=task.id,
                form_data=TaskUpdateForm(status=TaskStatus.FAILED.value, percentage=0, extras=task.extras),
            )
            raise FileNotSupported(f"Unsupported file type {content_type}")

        return pages

    def predict_on_pages(self, task: TaskModel, pages: List[Image.Image], save_image: bool = True) -> TaskModel:
        task = self.set_output(task=task, total_pages=len(pages))
        task.output.pages = [Page(page=i) for i in range(len(pages))]
        task.output.text = ""

        # Pages déjà extraites par liteparse (email/zip avec pièces jointes
        # bureautiques) : pas d'OCR, on récupère directement le texte connu.
        page_sources = getattr(pages, "page_sources", None)
        ocr_pages = getattr(pages, "ocr_pages", None)
        if page_sources is not None and ocr_pages is not None:
            task = self._fill_text_pages(task, pages, page_sources, ocr_pages, save_image=save_image)
            ocr_indices = sorted(ocr_pages)
        else:
            ocr_indices = list(range(len(pages)))

        if not ocr_indices:
            # Toutes les pages étaient déjà du texte connu (liteparse) : rien à OCR-iser.
            if not pages:
                task.output.set_text()
                return task
            return self._checkpoint_progress(task, len(pages))

        already_processed = len(pages) - len(ocr_indices)
        for start in range(0, len(ocr_indices), self.batch_size):
            batch_indices = ocr_indices[start : start + self.batch_size]
            task = self._predict_on_ocr_batch(task, pages, batch_indices, save_image=save_image)
            processed = already_processed + start + len(batch_indices)
            task = self._checkpoint_progress(task, processed)

        return task

    def _fill_text_pages(
        self,
        task: TaskModel,
        pages: List[Image.Image],
        page_sources: list,
        ocr_pages: set,
        save_image: bool = True,
    ) -> TaskModel:
        """Renseigne les pages déjà extraites par liteparse (pas d'OCR), en
        générant quand même leur image (déjà rendue par LazyEmailList /
        LazyZipList) pour exposer un page_url au même titre que les pages OCR."""
        for i, parsed in enumerate(page_sources):
            if i in ocr_pages or parsed is None:
                continue
            page_url = self._upload_page_image(task, pages[i], i) if save_image else None
            task.output.pages[i] = parsed_page_to_schema(parsed, page_url=page_url)
        return task

    def _predict_on_ocr_batch(
        self, task: TaskModel, pages: List[Image.Image], batch_indices: List[int], save_image: bool = True
    ) -> TaskModel:
        extra_log = {"task_id": task.id, "user_id": task.user_id}
        filename = task.input.raw_filename
        t_predict = time.time()
        batch = [pages[idx] for idx in batch_indices]
        logger.debug(
            f"[worker {self.name}] {filename} for task {task.id}, batch pages {batch_indices}[total: {len(pages)}]",
            extra=extra_log,
        )

        partial_result: List[Page] = [task.output.pages[idx] for idx in batch_indices]
        for model in self.models:
            logger.debug(
                f"[worker {self.name}][task-id {task.id}][model {model.__class__.__name__}][batch pages {batch_indices}][size result : {len(partial_result)}]",
                extra=extra_log,
            )
            model.set_current_task(task)
            t = time.time()
            partial_result = model.batch_predict(images=batch, pages=partial_result)
            logger.debug(
                f"[worker {self.name}][task-id {task.id}][model{model.__class__.__name__}][process time {time.time() - t:.2f}]",
                extra=extra_log,
            )

        if save_image:
            for j, idx in enumerate(batch_indices):
                partial_result[j].page_url = self._upload_page_image(task, batch[j], idx)

        for j, idx in enumerate(batch_indices):
            task.output.pages[idx] = partial_result[j]

        logger.debug(
            f"{filename} time to process pages {batch_indices} - {time.time() - t_predict:.2f}s",
            extra=extra_log,
        )
        return task

    def _upload_page_image(self, task: TaskModel, image: Image.Image, page_index: int) -> Optional[str]:
        client_s3 = self.file_connector.client
        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        buffer.seek(0)
        key = f"{task.user_id}/{task.id}/images/page_{page_index}.jpg"
        client_s3.upload_fileobj(buffer, self.file_connector.bucket_name, key)
        logger.debug(f"[worker {self.name}] Uploaded page {page_index} to {key}")
        return key

    def _checkpoint_progress(self, task: TaskModel, processed_pages: int) -> TaskModel:
        extra_log = {"task_id": task.id, "user_id": task.user_id}
        percentage = processed_pages / task.output.total_pages
        logger.debug(
            f"[worker {self.name}] [Current percentage {100 * percentage:.2f}%]",
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
        return task

    def set_output(self, task: TaskModel, total_pages: int = -1, pages: list[Page] = []) -> TaskModel:
        task = self.set_extras(task=task)
        if task.output is None:
            task.output = OCRResult(
                type=self.name,
                model_name=__name__,
                version=__version__,
                created_at=int(time.time()),
                updated_at=int(time.time()),
                total_pages=total_pages,
                pages=pages,
            )
        return task

    def _process_task(self, task: TaskModel) -> TaskModel:
        extra_log = {"task_id": task.id, "user_id": task.user_id}
        task = self.set_output(task=task)

        task = task_table.update_task(
            task_id=task.id,
            form_data=TaskUpdateForm(
                status=TaskStatus.IN_PROGRESS.value,
                percentage=0,
                extras=task.extras,
                input=task.input,
                output=task.output,
            ),
        )

        filename = task.input.raw_filename
        logger.debug(f"{task.id} - {task.user_id} - {filename} - {task.extras} ", extra=extra_log)
        content = self.get_content_file(task=task)
        content_hash = hash_file(content)
        task.content_hash = content_hash
        logger.debug(f"{task.id} - {content}", extra=extra_log)
        pages = self.transform_content(task=task, content=content)
        logger.debug(
            f"[worker {self.name}] Start to process - {filename} - {len(pages)}",
            extra=extra_log,
        )
        if self.cache:
            logger.debug(f"[worker {self.name}] Search into cache ", extra=extra_log)
            if self.cache.is_in_cache(task=task):
                cache_task = self.cache.get_task_from_cache(task=task)
                logger.debug(
                    f"[worker {self.name}] found into cache with status {cache_task.status} ",
                    extra=extra_log,
                )
                task.output.updated_at = int(time.time())
                task = task_table.update_task(
                    task_id=task.id,
                    form_data=TaskUpdateForm(
                        status=cache_task.status,
                        percentage=cache_task.percentage,
                        extras=cache_task.extras,
                        output=cache_task.output,
                        content_hash=content_hash,
                    ),
                )
                return task

        task.output.total_pages = len(pages)
        task.output.updated_at = int(time.time())
        task = task_table.update_task(
            task_id=task.id,
            form_data=TaskUpdateForm(
                status=TaskStatus.IN_PROGRESS.value,
                percentage=0,
                extras=task.extras,
                output=task.output,
                content_hash=content_hash,
            ),
        )

        try:
            task = self.predict_on_pages(task=task, pages=pages)
        except Exception as e:
            task.extras["error"] = str(e)
            task = task_table.update_task(
                task_id=task.id,
                form_data=TaskUpdateForm(
                    status=TaskStatus.FAILED.value,
                    percentage=task.percentage,
                    extras=task.extras,
                    content_hash=content_hash,
                ),
            )
            raise

        task = task_table.update_task(
            task_id=task.id,
            form_data=TaskUpdateForm(
                status=TaskStatus.COMPLETED.value,
                percentage=task.percentage,
                extras=task.extras,
                content_hash=content_hash,
            ),
        )
        logger.debug(f"[worker {self.name}] {task.id} - done")

        task = task_table.update_task(
            task_id=task.id,
            form_data=TaskUpdateForm(
                status=TaskStatus.COMPLETED.value,
                percentage=task.percentage,
                extras=task.extras,
                content_hash=content_hash,
            ),
        )

        # Only the uploaded file: the rendered page images stay available to the page viewer
        # until the task itself is deleted.
        try:
            self.file_connector.delete_by_s3_key(task.input.storage_file_path)
        except Exception as e:
            logger.warning(str(e))

        return task

    def process_task(self, task: TaskModel) -> TaskModel:
        t = time.time()

        current_task = self._process_task(task)
        logger.debug(
            f"[worker {self.name}] Processed task {current_task.id} with status {current_task.status} percentage {current_task.percentage} in {time.time() - t:.2f}s",
            extra={"task_id": current_task.id, "status": current_task.status},
        )

        return current_task


class AnyFileProcessWorker(BaseWorker):
    def is_applicable(self, task: TaskModel) -> bool:
        content_type = task.input.content_type
        return (
            content_type.startswith("image/")
            or content_type == "application/pdf"
            or content_type in EMAIL_CONTENT_TYPES
            or content_type in ZIP_CONTENT_TYPES
        )


class DefaultFileProcessWorker(BaseWorker):
    def is_applicable(self, task: TaskModel) -> bool:
        return task.type == TaskOperation.DEFAULT.value
