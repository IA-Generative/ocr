import pytest
from PIL import Image

from business.layout.worker import common
from business.layout.worker import table_worker as module
from business.layout.worker.table_worker import TableWorker
from business.layout.configs.layout import LayoutSettings
from services.base.model import BaseModelPrediction
from src.schemas.layout import Layout, TableContent
from src.schemas.output import Page
from src.schemas.task import LAYOUT_STATUS_KEY, TaskStatus
from src.utils.layout import TABLE_REGIONS_KEY

from fakes import FakeConnector, FakeTaskTable, make_task


class FakeTableModel(BaseModelPrediction):
    def __init__(self, fail: bool = False):
        super().__init__()
        self.fail = fail

    def batch_predict(self, images, pages=[], *args, **kwargs):
        if self.fail:
            raise RuntimeError("table exploded")
        for page in pages:
            for layout in page.tables:
                layout.table = TableContent(html="<table></table>", markdown="| a |", n_rows=1, n_cols=1)
        return pages


class SequencedTable(FakeTaskTable):
    """Le worker layout n'a pas encore écrit à la première lecture."""

    def __init__(self, task, layout_statuses):
        super().__init__(task, [])
        self.layout_statuses = layout_statuses

    def get_task_by_id(self, task_id):
        if self.layout_statuses:
            self.task.extras[LAYOUT_STATUS_KEY] = self.layout_statuses.pop(0)
        return self.task.model_copy(deep=True)


@pytest.fixture
def image_path(tmp_path):
    path = tmp_path / "src.png"
    Image.new("RGB", (40, 40), "white").save(path)
    return path


def build(monkeypatch, image_path, layout_statuses, model):
    task = make_task()
    task.status = TaskStatus.COMPLETED.value
    task.output.pages = [Page(page=0, tables=[Layout(cls_id=2, label="table", score=0.9, coordinate=[0, 0, 1, 1])])]
    fake_table = SequencedTable(task, layout_statuses)
    monkeypatch.setattr(common, "task_table", fake_table)
    monkeypatch.setattr(module, "task_table", fake_table)
    worker = TableWorker(
        name="table-worker",
        file_connector=FakeConnector(image_path),
        models=[model],
        settings=LayoutSettings(LAYOUT_WAIT_POLL_INTERVAL_S=0),
        sleep=lambda _: None,
    )
    message = make_task()
    message.extras = {TABLE_REGIONS_KEY: {"0": [[0, 0, 1, 1]]}}
    return worker, fake_table, message


def test_is_applicable_needs_regions():
    worker = TableWorker(name="w", file_connector=None, models=[])
    message = make_task()
    assert not worker.is_applicable(message)
    message.extras = {TABLE_REGIONS_KEY: {"0": [[0, 0, 1, 1]]}}
    assert worker.is_applicable(message)


def test_tables_wait_for_layout_then_merge(monkeypatch, image_path):
    worker, table, message = build(monkeypatch, image_path, ["pending", "pending", "partial"], FakeTableModel())

    worker.process_task(message)

    assert len(table.updates) == 1
    assert table.task.extras[LAYOUT_STATUS_KEY] == "completed"
    assert table.task.output.pages[0].tables[0].table.markdown == "| a |"


def test_table_error_keeps_layout_and_reports(monkeypatch, image_path):
    worker, table, message = build(monkeypatch, image_path, ["partial"], FakeTableModel(fail=True))

    worker.process_task(message)

    assert table.task.extras[LAYOUT_STATUS_KEY] == "completed"
    assert "table exploded" in table.task.extras["layout_error"]
    assert table.task.output.pages[0].tables[0].table is None


def test_tables_dropped_when_layout_failed(monkeypatch, image_path):
    worker, table, message = build(monkeypatch, image_path, ["failed"], FakeTableModel())

    worker.process_task(message)

    assert table.updates == []
