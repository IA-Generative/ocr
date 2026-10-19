from business.layout.utils.table import build_table_content, parse_table_html

SIMPLE = (
    "<html><body><table><tbody>"
    "<tr><td>Nom</td><td>Age</td></tr>"
    "<tr><td>Alice</td><td>30</td></tr>"
    "</tbody></table></body></html>"
)

WITH_SPANS = (
    "<table>"
    "<tr><th rowspan='2'>A</th><th colspan='2'>B</th></tr>"
    "<tr><td>b1</td><td>b2</td></tr>"
    "<tr><td>x</td><td>y</td><td>z</td></tr>"
    "</table>"
)


def test_simple_table_grid():
    cells, n_rows, n_cols = parse_table_html(SIMPLE)
    assert (n_rows, n_cols) == (2, 2)
    assert [(c.row, c.col, c.text) for c in cells] == [(0, 0, "Nom"), (0, 1, "Age"), (1, 0, "Alice"), (1, 1, "30")]


def test_spans_are_placed_on_the_grid():
    cells, n_rows, n_cols = parse_table_html(WITH_SPANS)
    assert (n_rows, n_cols) == (3, 3)
    by_text = {c.text: c for c in cells}
    assert (by_text["A"].row, by_text["A"].col, by_text["A"].rowspan) == (0, 0, 2)
    assert (by_text["B"].col, by_text["B"].colspan) == (1, 2)
    # b1/b2 sont décalés par le rowspan de A
    assert (by_text["b1"].row, by_text["b1"].col) == (1, 1)
    assert (by_text["b2"].row, by_text["b2"].col) == (1, 2)
    assert by_text["A"].is_header


def test_markdown_and_escape():
    content = build_table_content("<table><tr><td>a|b</td><td>c<br>d</td></tr><tr><td>1</td><td>2</td></tr></table>")
    assert content.markdown.splitlines() == ["| a\\|b | c d |", "| --- | --- |", "| 1 | 2 |"]


def test_cell_boxes_only_when_counts_match():
    boxes = [[0.1, 0.1, 0.2, 0.2]] * 4
    assert build_table_content(SIMPLE, cell_boxes=boxes).cells[0].bbox == [0.1, 0.1, 0.2, 0.2]
    assert build_table_content(SIMPLE, cell_boxes=boxes[:3]).cells[0].bbox is None


def test_empty_or_invalid_html():
    content = build_table_content("")
    assert (content.n_rows, content.n_cols, content.cells, content.markdown) == (0, 0, [], "")
