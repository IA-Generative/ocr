import pytest
from PIL import Image

from business.layout.configs.layout import LayoutSettings
from business.layout.worker import common
from business.layout.worker import layout_worker as module
from business.layout.worker.layout_worker import LayoutWorker
from fakes import FakeConnector, FakeLayoutModel, FakeTaskTable, make_task
from src.schemas.task import LAYOUT_STATUS_KEY, TaskStatus


@pytest.fixture
def image_path(tmp_path):
    path = tmp_path / "src.png"
    Image.new("RGB", (40, 40), "white").save(path)
    return path


def build_worker(monkeypatch, image_path, statuses, model, dispatched=None):
    fake_table = FakeTaskTable(make_task(), statuses)
    monkeypatch.setattr(module, "task_table", fake_table)
    monkeypatch.setattr(common, "task_table", fake_table)
    connector = FakeConnector(image_path)
    worker = LayoutWorker(
        name="layout-worker",
        file_connector=connector,
        models=[model],
        settings=LayoutSettings(LAYOUT_WAIT_POLL_INTERVAL_S=0),
        sleep=lambda _: None,
        dispatch_tables=(lambda task, regions: dispatched.append(regions)) if dispatched is not None else None,
    )
    return worker, fake_table, connector


def test_is_applicable():
    worker = LayoutWorker(name="w", file_connector=None, models=[])
    task = make_task()
    assert worker.is_applicable(task)
    task.input.content_type = "text/csv"
    assert not worker.is_applicable(task)
    task.input.content_type = "application/pdf"
    task.type = "docling"
    assert not worker.is_applicable(task)


def test_layout_waits_for_ocr_then_merges(monkeypatch, image_path):
    statuses = ["in_progress", "in_progress", "completed"]
    worker, table, connector = build_worker(monkeypatch, image_path, statuses, FakeLayoutModel())

    worker.process_task(make_task())

    # une seule écriture, et seulement une fois l'OCR terminé
    assert len(table.updates) == 1
    assert table.task.status == TaskStatus.COMPLETED.value
    assert table.task.extras[LAYOUT_STATUS_KEY] == "completed"
    assert table.task.extras["keep"] == "me"
    page = table.task.output.pages[0]
    assert page.layouts[0].label == "image" and len(page.images) == 1
    assert "u1/t1/layout/a.png" in connector.deleted


def test_layout_error_does_not_fail_the_task(monkeypatch, image_path):
    worker, table, _ = build_worker(monkeypatch, image_path, ["completed"], FakeLayoutModel(fail=True))

    worker.process_task(make_task())

    assert table.task.status == TaskStatus.COMPLETED.value
    assert table.task.extras[LAYOUT_STATUS_KEY] == "failed"
    assert "model exploded" in table.task.extras["layout_error"]
    assert table.task.output.pages[0].layouts == []


def test_layout_dropped_when_ocr_fails(monkeypatch, image_path):
    worker, table, _ = build_worker(monkeypatch, image_path, ["failed"], FakeLayoutModel())

    worker.process_task(make_task())

    assert table.task.status == TaskStatus.FAILED.value
    assert table.task.extras[LAYOUT_STATUS_KEY] == "failed"
    assert table.task.output.pages[0].layouts == []


def test_timeout_writes_nothing(monkeypatch, image_path):
    worker, table, _ = build_worker(monkeypatch, image_path, [], FakeLayoutModel())
    worker.settings.LAYOUT_WAIT_OCR_TIMEOUT_S = 0

    worker.process_task(make_task())

    assert table.updates == []


def test_tables_are_dispatched_and_status_is_partial(monkeypatch, image_path):
    dispatched = []
    model = FakeLayoutModel(with_table=True)
    worker, table, _ = build_worker(monkeypatch, image_path, ["completed"], model, dispatched=dispatched)

    worker.process_task(make_task())

    assert dispatched == [{0: [[0.2, 0.2, 0.8, 0.6]]}]
    assert table.task.extras[LAYOUT_STATUS_KEY] == "partial"
    assert len(table.task.output.pages[0].tables) == 1
    assert table.task.output.pages[0].tables[0].table is None


def test_tables_not_dispatched_when_disabled(monkeypatch, image_path):
    dispatched = []
    worker, table, _ = build_worker(
        monkeypatch, image_path, ["completed"], FakeLayoutModel(with_table=True), dispatched
    )
    worker.settings.LAYOUT_ENABLE_TABLES = False

    worker.process_task(make_task())

    assert dispatched == []
    assert table.task.extras[LAYOUT_STATUS_KEY] == "completed"
