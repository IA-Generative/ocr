import os
import time
from typing import Callable, Iterable, List, Optional

from PIL import Image

from business.layout.configs.layout import LayoutSettings
from services.base.cache import BaseCache
from services.base.model import BaseModelPrediction
from services.base.worker import BaseWorker, LayoutNotApplicable
from services.utils.lazy_pdf import LazyPdfImageList
from src.connector.s3_connector import S3Connector
from src.logger import logger
from src.schemas.task import (
    LAYOUT_STATUS_KEY,
    LayoutStatus,
    TaskModel,
    TaskOperation,
    TaskStatus,
    TaskUpdateForm,
    task_table,
)
from src.utils.layout import is_layout_content_type

# Statuts après lesquels l'OCR n'écrira plus jamais dans la tâche.
OCR_FINAL_STATUSES = frozenset(
    {
        TaskStatus.COMPLETED.value,
        TaskStatus.FAILED.value,
        TaskStatus.CANCELED.value,
        TaskStatus.TIMEOUT.value,
    }
)


class LayoutPipelineWorker(BaseWorker):
    """Socle des workers layout / table : un modèle par worker, exécutés en parallèle de l'OCR.

    Ces workers calculent en mémoire et ne fusionnent dans ``output`` qu'une fois qu'aucun autre
    process n'écrit plus dedans (voir ``_wait_for``). Une erreur ne fait jamais échouer la tâche :
    elle est reportée dans ``extras.layout_status`` / ``extras.layout_error``.
    """

    def __init__(
        self,
        name: str,
        file_connector: S3Connector,
        models: List[BaseModelPrediction],
        batch_size: int = 2,
        worker_weight: int | float = 1,
        cache: Optional[BaseCache] = None,
        settings: LayoutSettings | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ):
        super().__init__(
            name,
            file_connector,
            models=models,
            batch_size=batch_size,
            worker_weight=worker_weight,
            cache=cache,
        )
        self.settings = settings or LayoutSettings()
        self._sleep = sleep

    def is_applicable(self, task: TaskModel) -> bool:
        return (
            task.type == TaskOperation.DEFAULT.value
            and task.input is not None
            and is_layout_content_type(task.input.content_type)
        )

    def transform_content(self, task: TaskModel, content: str) -> List[Image.Image]:
        if task.input.content_type == "application/pdf":
            return LazyPdfImageList(content, dpi=self.settings.LAYOUT_PDF_DPI)
        if task.input.content_type.startswith("image/"):
            return [Image.open(content).convert("RGB")]
        raise LayoutNotApplicable(f"No layout for content type {task.input.content_type}")

    def _load_pages(self, task: TaskModel) -> tuple[str, List[Image.Image]]:
        # Pas de get_content_file : sur erreur il passerait toute la tâche en FAILED.
        content = self.file_connector.download_by_s3_key(s3_key=task.input.storage_file_path)
        try:
            return content, self.transform_content(task=task, content=content)
        except Exception:
            self._remove_file(content)
            raise

    @staticmethod
    def _remove_file(path: str) -> None:
        if isinstance(path, str) and os.path.exists(path):
            os.remove(path)

    def _wait_for(self, task: TaskModel, is_ready: Callable[[TaskModel], bool]) -> Optional[TaskModel]:
        """Attend que ``is_ready(tâche en base)`` soit vrai ; ``None`` si la tâche a disparu ou au timeout."""
        deadline = time.time() + self.settings.LAYOUT_WAIT_OCR_TIMEOUT_S
        while True:
            current = task_table.get_task_by_id(task.id)
            if current is None:
                return None
            if is_ready(current):
                return current
            if time.time() >= deadline:
                logger.warning(f"[worker {self.name}] timeout while waiting on task {task.id}")
                return None
            self._sleep(self.settings.LAYOUT_WAIT_POLL_INTERVAL_S)

    def _wait_for_ocr(self, task: TaskModel) -> Optional[TaskModel]:
        return self._wait_for(task, lambda current: current.status in OCR_FINAL_STATUSES)

    def _set_layout_status(self, task_id: str, status: LayoutStatus, error: Optional[str] = None) -> None:
        try:
            # Relit les extras en base (jamais ceux du message) pour ne modifier que le statut layout.
            current = task_table.get_task_by_id(task_id)
            if current is None:
                return
            extras = dict(current.extras or {})
            extras[LAYOUT_STATUS_KEY] = status.value
            if error:
                extras["layout_error"] = error
            task_table.update_task(task_id=task_id, form_data=TaskUpdateForm(extras=extras))
        except Exception as e:
            logger.error(f"[worker {self.name}] cannot set layout status for task {task_id}: {e}")

    def _delete_input_copy(self, task: TaskModel) -> None:
        """Supprime la copie du fichier source faite pour ce worker."""
        try:
            if task.input and task.input.storage_file_path:
                self.file_connector.client.delete_object(
                    Bucket=self.file_connector.bucket_name, Key=task.input.storage_file_path
                )
        except Exception as e:
            logger.warning(f"[worker {self.name}] cannot delete input copy: {e}")

    def _page_indices(self, total: int) -> Iterable[range]:
        for start in range(0, total, self.batch_size):
            yield range(start, min(start + self.batch_size, total))
