"""Public model surface for the OCR SDK.

The actual schemas live in `ocr_sdk/schemas/`, a field-for-field mirror of the
backend's `apps/server/src/schemas/*.py` (see `tests/ocr_sdk/test_models.py`, which
asserts `model_json_schema()` equality against the real backend schemas to catch
drift). This module just re-exports the ones SDK users need, plus a couple of
SDK-only shapes that don't correspond to a single backend pydantic model
(`PaginatedTasks`, `ProcessResponse`).
"""

from typing import Any, Dict
from pydantic import BaseModel, ConfigDict

from ocr_sdk.schemas.box import BaseBox, Bbox, Checkbox
from ocr_sdk.schemas.layout import Layout, TableCell, TableContent
from ocr_sdk.schemas.template import FormEntry, LLMFormField, ImageFormDetector
from ocr_sdk.schemas.vector import Vector
from ocr_sdk.schemas.input import InputForm, RegionOfInterest
from ocr_sdk.schemas.output import Page, OCRResult
from ocr_sdk.schemas.health import Health
from ocr_sdk.schemas.audio import AudioTranscriptionResult
from ocr_sdk.schemas.video import VideoDescriptionResult
from ocr_sdk.schemas.task import (
    TaskModel,
    TaskOutput,
    TaskStatus,
    TaskOperation,
    LayoutStatus,
    TaskStats,
    TaskStatsGlobal,
    TaskStatsUser,
)
from ocr_sdk.schemas.pagination import Pagination

__all__ = [
    "BaseBox",
    "Bbox",
    "Checkbox",
    "Layout",
    "TableCell",
    "TableContent",
    "FormEntry",
    "LLMFormField",
    "ImageFormDetector",
    "Vector",
    "InputForm",
    "RegionOfInterest",
    "Page",
    "OCRResult",
    "Health",
    "AudioTranscriptionResult",
    "VideoDescriptionResult",
    "TaskModel",
    "TaskOutput",
    "TaskStatus",
    "TaskOperation",
    "LayoutStatus",
    "TaskStats",
    "TaskStatsGlobal",
    "TaskStatsUser",
    "Pagination",
    "PaginatedTasks",
    "ProcessResponse",
]


class PaginatedTasks(Pagination[TaskModel]):
    """`GET /tasks/user/` response shape."""

    model_config = ConfigDict(from_attributes=True)


class ProcessResponse(BaseModel):
    """`PUT /process` response item - SDK-only shape, not a backend pydantic
    response_model (that endpoint returns a plain ``JSONResponse`` list of dicts)."""

    model_config = ConfigDict(from_attributes=True)
    page_content: str
    metadata: Dict[str, Any]
