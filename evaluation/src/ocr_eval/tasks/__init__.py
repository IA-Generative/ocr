from ocr_eval.tasks.base import Task
from ocr_eval.tasks.ocr import OcrTask

# Add new tasks (layout, tables, ...) here.
TASKS: dict[str, type[Task]] = {"ocr": OcrTask}

__all__ = ["TASKS", "OcrTask", "Task"]
