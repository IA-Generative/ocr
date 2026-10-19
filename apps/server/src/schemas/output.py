from typing import List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field
from src.schemas.box import Bbox, Checkbox
from src.schemas.layout import Layout
from src.utils.bboxes import sort_bboxes_reading_order, get_text_from_list_bboxes
from src.schemas.template import LLMFormField, ImageFormDetector, FormEntry
from src.schemas.vector import Vector


class Page(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    page: int
    page_url: Optional[str] = None
    boxes: List[Bbox] = Field(default_factory=list, description="Detections")
    layouts: List[Layout] = Field(default_factory=list, description="Layout definition")
    tables: List[Layout] = Field(default_factory=list, description="Layout regions of type table, with their structure")
    images: List[Layout] = Field(
        default_factory=list, description="Layout regions of type image/chart/seal (bbox only)"
    )
    formulas: List[Layout] = Field(default_factory=list, description="Layout regions of type formula (bbox only)")
    checkboxes: List[Checkbox] = Field(default_factory=list, description="Checkbox definition")
    form_entries: List[Union[LLMFormField, FormEntry]] = Field(default_factory=list, description="Form extraction")
    image_form_detector: Optional[ImageFormDetector] = Field(
        default=None, description="Détection de formulaire d'image"
    )
    vector: Optional[Vector] = Field(None, description="Vector representation of the page")
    similar_template_ids: List[tuple[str, float]] = Field(
        default_factory=list, description="List of similar template IDs"
    )
    page_markdown: Optional[str] = Field(default=None, description="Markdown content of the page (PP-StructureV3)")


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

    def set_page_text(self, page: Page, delta_y: float = 0.005) -> str:
        if page.page_markdown:
            return page.page_markdown

        page_lines_content = []
        checkboxes = [
            Bbox(
                x=checkbox.x,
                y=checkbox.y,
                confidence=checkbox.confidence,
                height=checkbox.height,
                width=checkbox.width,
                text="[x]" if checkbox.is_checked else "[ ]",
            )
            for checkbox in page.checkboxes
        ]

        sorted_bboxes = sort_bboxes_reading_order(bboxes=page.boxes + checkboxes, delta_y=delta_y)
        for line_sorted_boxes in sorted_bboxes:
            text_line = get_text_from_list_bboxes(line_sorted_boxes)
            page_lines_content.append(text_line)

        page_content = "\n".join(page_lines_content)
        return page_content

    def set_text(self, delta_y: float = 0.005):
        self.text = ""
        pages_content_per_page = []

        for i, page in enumerate(self.pages):
            page_lines_content = f"{20 * '-'} Page: {i + 1} {20 * '-'}\n"
            page_content = page_lines_content + self.set_page_text(page, delta_y=delta_y)
            pages_content_per_page.append(page_content)

        self.text = "\n".join(pages_content_per_page)
