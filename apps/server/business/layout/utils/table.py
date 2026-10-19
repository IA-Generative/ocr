from html.parser import HTMLParser
from typing import Optional, Sequence

from src.schemas.layout import TableCell, TableContent


class _TableHTMLParser(HTMLParser):
    """Parse un tableau HTML plat (les tableaux imbriqués sont aplatis dans la cellule parente)."""

    def __init__(self):
        super().__init__()
        self.rows: list[list[dict]] = []
        self._cell: Optional[dict] = None
        self._depth = 0

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self._depth += 1
        elif tag == "tr" and self._depth <= 1:
            self.rows.append([])
        elif tag in ("td", "th") and self._depth <= 1:
            if not self.rows:
                self.rows.append([])
            attributes = dict(attrs)
            self._cell = {
                "text": [],
                "is_header": tag == "th",
                "rowspan": _to_span(attributes.get("rowspan")),
                "colspan": _to_span(attributes.get("colspan")),
            }
        elif tag == "br" and self._cell is not None:
            self._cell["text"].append(" ")

    def handle_endtag(self, tag):
        if tag == "table":
            self._depth = max(0, self._depth - 1)
        elif tag in ("td", "th") and self._cell is not None and self._depth <= 1:
            self._cell["text"] = " ".join("".join(self._cell["text"]).split())
            self.rows[-1].append(self._cell)
            self._cell = None

    def handle_data(self, data):
        if self._cell is not None:
            self._cell["text"].append(data)


def _to_span(value: Optional[str]) -> int:
    try:
        return max(1, int(value))
    except (TypeError, ValueError):
        return 1


def parse_table_html(html: str) -> tuple[list[TableCell], int, int]:
    """Place chaque cellule sur la grille en tenant compte des rowspan/colspan.

    Returns:
        (cells, n_rows, n_cols)
    """
    parser = _TableHTMLParser()
    parser.feed(html or "")
    parser.close()

    occupied: set[tuple[int, int]] = set()
    cells: list[TableCell] = []
    n_cols = 0
    for row_index, row in enumerate(parser.rows):
        col_index = 0
        for raw in row:
            while (row_index, col_index) in occupied:
                col_index += 1
            for r in range(raw["rowspan"]):
                for c in range(raw["colspan"]):
                    occupied.add((row_index + r, col_index + c))
            cells.append(
                TableCell(
                    row=row_index,
                    col=col_index,
                    rowspan=raw["rowspan"],
                    colspan=raw["colspan"],
                    text=raw["text"],
                    is_header=raw["is_header"],
                )
            )
            col_index += raw["colspan"]
            n_cols = max(n_cols, col_index)

    n_rows = max((cell.row + cell.rowspan for cell in cells), default=0)
    return cells, n_rows, n_cols


def cells_to_markdown(cells: Sequence[TableCell], n_rows: int, n_cols: int) -> str:
    """Markdown GFM : les cellules fusionnées ne sont écrites que dans leur case d'origine."""
    if not n_rows or not n_cols:
        return ""

    grid = [["" for _ in range(n_cols)] for _ in range(n_rows)]
    for cell in cells:
        grid[cell.row][cell.col] = cell.text.replace("|", "\\|")

    lines = ["| " + " | ".join(grid[0]) + " |", "| " + " | ".join(["---"] * n_cols) + " |"]
    lines.extend("| " + " | ".join(row) + " |" for row in grid[1:])
    return "\n".join(lines)


def build_table_content(
    html: str,
    cell_boxes: Optional[Sequence[Sequence[float]]] = None,
) -> TableContent:
    """Construit le ``TableContent`` à partir du HTML produit par le modèle.

    ``cell_boxes`` : boîtes déjà normalisées sur la page, dans l'ordre des cellules du HTML.
    Elles sont ignorées si leur nombre ne correspond pas à celui des cellules.
    """
    cells, n_rows, n_cols = parse_table_html(html)
    if cell_boxes is not None and len(cell_boxes) == len(cells):
        for cell, box in zip(cells, cell_boxes):
            cell.bbox = [float(v) for v in box]
    return TableContent(
        html=html,
        markdown=cells_to_markdown(cells, n_rows, n_cols),
        n_rows=n_rows,
        n_cols=n_cols,
        cells=cells,
    )
