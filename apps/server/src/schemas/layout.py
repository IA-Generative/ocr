from typing import Optional, Any
from pydantic import BaseModel, Field


# labels
# document title, paragraph title, text, page number, abstract, table, references,
# footnotes, header, footer, algorithm, formula, formula number, image,
# table, seal, figure_table title, chart, and sidebar text and lists of references


class TableCell(BaseModel):
    row: int = Field(..., description="Index (0-based) of the first row covered by the cell.")
    col: int = Field(..., description="Index (0-based) of the first column covered by the cell.")
    rowspan: int = 1
    colspan: int = 1
    text: str = ""
    is_header: bool = False
    bbox: Optional[list[float]] = Field(
        default=None,
        description="Normalized [xmin, ymin, xmax, ymax] on the page, when the model provides it.",
    )


class TableContent(BaseModel):
    html: str = Field(..., description="Table as HTML, text included.")
    markdown: str = Field("", description="Table as GitHub-flavored markdown (spans are flattened).")
    n_rows: int = 0
    n_cols: int = 0
    cells: list[TableCell] = Field(default_factory=list)


class Layout(BaseModel):
    cls_id: int = Field(..., description="Class ID, an integer.")
    label: str = Field(..., description="Class label, a string.")
    score: float = Field(..., description="Confidence score of the bounding box, a float.")
    coordinate: list[float] = Field(
        ...,
        description="Coordinates of the bounding box, a list of floats in the format [xmin, ymin, xmax, ymax]",
    )
    content: Optional[Any] = None
    table: Optional[TableContent] = Field(default=None, description="Structured content, only for `table` regions.")
