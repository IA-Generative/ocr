"""OCR SDK - Python client for OCR API."""

from ocr_sdk.client_async import AsyncOCRClient
from ocr_sdk.client_sync import SyncOCRClient
from ocr_sdk.models import (
    TaskModel,
    TaskStatus,
    TaskOperation,
    LayoutStatus,
    Health,
    OCRResult,
    Page,
    Bbox,
    Checkbox,
    Layout,
    TableCell,
    TableContent,
    FormEntry,
    LLMFormField,
    ImageFormDetector,
    Vector,
    PaginatedTasks,
    TaskStats,
    ProcessResponse,
)

__version__ = "0.2.0"

__all__ = [
    "AsyncOCRClient",
    "SyncOCRClient",
    "TaskModel",
    "TaskStatus",
    "TaskOperation",
    "LayoutStatus",
    "Health",
    "OCRResult",
    "Page",
    "Bbox",
    "Checkbox",
    "Layout",
    "TableCell",
    "TableContent",
    "FormEntry",
    "LLMFormField",
    "ImageFormDetector",
    "Vector",
    "PaginatedTasks",
    "TaskStats",
    "ProcessResponse",
]
