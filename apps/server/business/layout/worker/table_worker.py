import time
import traceback
from typing import Optional

from business.layout.worker.common import LayoutPipelineWorker
from src.logger import logger
from src.schemas.layout import Layout
from src.schemas.output import Page
from src.schemas.task import LAYOUT_STATUS_KEY, LayoutStatus, TaskModel, TaskUpdateForm, task_table
from src.utils.layout import TABLE_REGIONS_KEY


class TableWorker(LayoutPipelineWorker):
    """Structure et texte des tables, dans un worker (et un process) dédié au modèle de tables.

    Les bbox des tables viennent du worker ``layout`` (``extras.table_regions`` du message). Le
    calcul se fait en parallèle de l'OCR ; la fusion attend que le worker ``layout`` ait écrit les
    zones (``layout_status == partial``), jamais avant : c'est ce qui sérialise les deux écritures.
    """

    def is_applicable(self, task: TaskModel) -> bool:
        return super().is_applicable(task) and bool((task.extras or {}).get(TABLE_REGIONS_KEY))

    def process_task(self, task: TaskModel) -> TaskModel:
        started = time.time()
        results: dict[int, list[Layout]] = {}
        error: Optional[str] = None
        try:
            results = self._compute_tables(task)
        except Exception as e:
            error = str(e)
            logger.error(f"[worker {self.name}] tables failed for task {task.id}: {e}\n{traceback.format_exc()}")

        try:
            ready = self._wait_for(task, self._layout_written)
            if ready is None:
                logger.warning(f"[worker {self.name}] task {task.id} gone or layout never written, tables dropped")
            elif ready.extras.get(LAYOUT_STATUS_KEY) == LayoutStatus.FAILED.value:
                logger.warning(f"[worker {self.name}] layout failed for task {task.id}, tables dropped")
            else:
                self._merge_into_task(task.id, results, error)
                logger.info(f"[worker {self.name}] task {task.id} tables merged in {time.time() - started:.2f}s")
        except Exception as e:
            logger.error(f"[worker {self.name}] cannot merge tables of task {task.id}: {e}\n{traceback.format_exc()}")
            self._set_layout_status(task.id, LayoutStatus.COMPLETED, error=f"table structure failed: {e}")
        finally:
            self._delete_input_copy(task)
        return task

    @staticmethod
    def _layout_written(current: TaskModel) -> bool:
        status = (current.extras or {}).get(LAYOUT_STATUS_KEY)
        return status in (LayoutStatus.PARTIAL.value, LayoutStatus.COMPLETED.value, LayoutStatus.FAILED.value)

    def _compute_tables(self, task: TaskModel) -> dict[int, list[Layout]]:
        regions = {int(k): v for k, v in task.extras[TABLE_REGIONS_KEY].items()}
        content, pages = self._load_pages(task)
        try:
            results: dict[int, list[Layout]] = {}
            for index in sorted(regions):
                if index >= len(pages):
                    continue
                table_page = Page(
                    page=index,
                    tables=[Layout(cls_id=0, label="table", score=1.0, coordinate=list(box)) for box in regions[index]],
                )
                for model in self.models:
                    model.set_current_task(task)
                    table_page = model.batch_predict(images=[pages[index]], pages=[table_page])[0]
                results[index] = table_page.tables
            return results
        finally:
            self._remove_file(content)

    def _merge_into_task(self, task_id: str, results: dict[int, list[Layout]], error: Optional[str]) -> None:
        current = task_table.get_task_by_id(task_id)
        if current is None or current.output is None:
            raise RuntimeError(f"Task {task_id} has no output to attach the tables to")

        for index, computed in results.items():
            if index >= len(current.output.pages):
                continue
            page = current.output.pages[index]
            if len(page.tables) != len(computed):
                logger.warning(f"[worker {self.name}] task {task_id} page {index}: table count mismatch, skipped")
                continue
            for target, source in zip(page.tables, computed):
                target.table = source.table

        extras = dict(current.extras or {})
        extras[LAYOUT_STATUS_KEY] = LayoutStatus.COMPLETED.value
        if error:
            extras["layout_error"] = f"table structure failed: {error}"
        task_table.update_task(task_id=task_id, form_data=TaskUpdateForm(output=current.output, extras=extras))
