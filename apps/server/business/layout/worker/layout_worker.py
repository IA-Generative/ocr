import json
import os
import time
import traceback
from typing import Callable, List, Optional

from business.layout.worker.common import LayoutPipelineWorker
from src.logger import logger
from src.schemas.output import Page
from src.schemas.task import LayoutStatus, TaskModel, TaskStatus, TaskUpdateForm, task_table
from src.utils.layout import TABLE_QUEUE, TABLE_REGIONS_KEY, TABLE_WORKER_NAME

# {index de page: [bbox normalisées des tables]}
TableRegions = dict[int, list[list[float]]]


class LayoutWorker(LayoutPipelineWorker):
    """Détection des zones de la page (layouts, images, formules), en parallèle de l'OCR.

    1. Calcule en mémoire les zones de chaque page (aucune écriture en base).
    2. S'il y a des tables, les confie tout de suite au worker ``table`` (autre modèle, autre
       process), qui travaille en parallèle de l'OCR et de ce worker.
    3. Attend la fin de l'OCR, puis fusionne les zones dans ``output``. ``layout_status`` passe à
       ``partial`` tant que le worker ``table`` n'a pas fini (c'est lui qui le passe à
       ``completed``), sinon à ``completed``.
    """

    def __init__(self, *args, dispatch_tables: Optional[Callable[[TaskModel, TableRegions], None]] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._dispatch_tables = dispatch_tables or self._send_to_table_worker

    def process_task(self, task: TaskModel) -> TaskModel:
        started = time.time()
        layout_pages: Optional[List[Page]] = None
        error: Optional[str] = None
        tables_dispatched = False
        try:
            layout_pages = self._compute_layout(task)
            regions = self._table_regions(layout_pages)
            if regions and self.settings.LAYOUT_ENABLE_TABLES:
                self._dispatch_tables(task, regions)
                tables_dispatched = True
        except Exception as e:
            error = str(e)
            logger.error(f"[worker {self.name}] layout failed for task {task.id}: {e}\n{traceback.format_exc()}")

        try:
            # L'OCR réécrit `extras` à chaque étape : tant qu'il tourne, rien de ce que le layout écrirait
            # n'est durable. On attend donc sa fin y compris pour reporter une erreur.
            ocr_task = self._wait_for_ocr(task)
            if ocr_task is None:
                logger.warning(f"[worker {self.name}] task {task.id} gone or OCR still running, layout dropped")
            elif ocr_task.status != TaskStatus.COMPLETED.value:
                self._set_layout_status(task.id, LayoutStatus.FAILED, error=f"OCR ended with status {ocr_task.status}")
            elif error is not None:
                self._set_layout_status(task.id, LayoutStatus.FAILED, error=error)
            else:
                self._merge_into_task(task.id, layout_pages, tables_pending=tables_dispatched)
                logger.info(f"[worker {self.name}] task {task.id} layout merged in {time.time() - started:.2f}s")
        except Exception as e:
            logger.error(f"[worker {self.name}] cannot merge layout of task {task.id}: {e}\n{traceback.format_exc()}")
            self._set_layout_status(task.id, LayoutStatus.FAILED, error=str(e))
        finally:
            self._delete_input_copy(task)
        return task

    def _compute_layout(self, task: TaskModel) -> List[Page]:
        content, pages = self._load_pages(task)
        try:
            layout_pages = [Page(page=i) for i in range(len(pages))]
            for indices in self._page_indices(len(pages)):
                batch = [pages[i] for i in indices]
                partial = [layout_pages[i] for i in indices]
                for model in self.models:
                    model.set_current_task(task)
                    partial = model.batch_predict(images=batch, pages=partial)
                for i, page in zip(indices, partial):
                    layout_pages[i] = page
            return layout_pages
        finally:
            self._remove_file(content)

    @staticmethod
    def _table_regions(layout_pages: List[Page]) -> TableRegions:
        return {i: [list(t.coordinate) for t in page.tables] for i, page in enumerate(layout_pages) if page.tables}

    def _send_to_table_worker(self, task: TaskModel, regions: TableRegions) -> None:
        """Envoie la tâche au worker ``table`` avec sa propre copie du fichier (chacun supprime la sienne)."""
        from src.connector.broker_connector import celery_app  # noqa: PLC0415

        client = self.file_connector.client
        table_key = f"{task.user_id}/{task.id}/table/{os.path.basename(task.input.storage_file_path)}"
        client.copy_object(
            Bucket=self.file_connector.bucket_name,
            Key=table_key,
            CopySource={"Bucket": self.file_connector.bucket_name, "Key": task.input.storage_file_path},
        )
        table_task = task.model_copy(deep=True)
        table_task.input.storage_file_path = table_key
        table_task.extras = {**(table_task.extras or {}), TABLE_REGIONS_KEY: {str(k): v for k, v in regions.items()}}
        celery_app.send_task(
            TABLE_WORKER_NAME,
            args=[json.dumps(table_task.model_dump())],
            task_id=f"{task.id}-table",
            queue=TABLE_QUEUE,
        )

    def _merge_into_task(self, task_id: str, layout_pages: List[Page], tables_pending: bool) -> None:
        current = task_table.get_task_by_id(task_id)
        if current is None or current.output is None:
            raise RuntimeError(f"Task {task_id} has no OCR output to attach the layout to")

        ocr_pages = current.output.pages
        if len(ocr_pages) != len(layout_pages):
            logger.warning(
                f"[worker {self.name}] task {task_id}: {len(ocr_pages)} OCR pages vs {len(layout_pages)} layout pages"
            )
        for ocr_page, layout_page in zip(ocr_pages, layout_pages):
            ocr_page.layouts = layout_page.layouts
            ocr_page.tables = layout_page.tables
            ocr_page.images = layout_page.images
            ocr_page.formulas = layout_page.formulas

        extras = dict(current.extras or {})
        extras["layout_status"] = (LayoutStatus.PARTIAL if tables_pending else LayoutStatus.COMPLETED).value
        extras.pop("layout_error", None)
        task_table.update_task(task_id=task_id, form_data=TaskUpdateForm(output=current.output, extras=extras))
