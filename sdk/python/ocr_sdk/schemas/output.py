from typing import List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field
from ocr_sdk.schemas.box import Bbox, Checkbox
from ocr_sdk.schemas.layout import Layout
from ocr_sdk.schemas.template import LLMFormField, ImageFormDetector, FormEntry
from ocr_sdk.schemas.vector import Vector


class Page(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    page: int
    page_url: Optional[str] = None
    boxes: List[Bbox] = Field(default_factory=list, description="Detections")
    layouts: List[Layout] = Field(default_factory=list, description="Layout definition")
    tables: List[Layout] = Field(
        default_factory=list,
        description="Layout regions of type table, with their structure",
    )
    images: List[Layout] = Field(
        default_factory=list,
        description="Layout regions of type image/chart/seal (bbox only)",
    )
    formulas: List[Layout] = Field(
        default_factory=list,
        description="Layout regions of type formula (bbox only)",
    )
    checkboxes: List[Checkbox] = Field(
        default_factory=list, description="Checkbox definition"
    )
    form_entries: List[Union[LLMFormField, FormEntry]] = Field(
        default_factory=list, description="Form extraction"
    )
    image_form_detector: Optional[ImageFormDetector] = Field(
        default=None, description="Détection de formulaire d'image"
    )
    vector: Optional[Vector] = Field(
        None, description="Vector representation of the page"
    )
    similar_template_ids: List[tuple[str, float]] = Field(
        default_factory=list, description="List of similar template IDs"
    )
    page_markdown: Optional[str] = Field(
        default=None, description="Markdown content of the page (PP-StructureV3)"
    )


class OCRResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    type: str
    model_name: str
    created_at: int
    updated_at: int
    version: str
    total_pages: int
    pages: List[Page]
    extras: Optional[dict] = None
    text: Optional[str] = ""
