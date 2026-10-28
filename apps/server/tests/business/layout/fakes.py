from types import SimpleNamespace

from src.schemas.input import InputForm
from src.schemas.layout import Layout
from src.schemas.output import OCRResult, Page
from src.schemas.task import LAYOUT_STATUS_KEY, TaskModel, TaskStatus
from services.base.model import BaseModelPrediction


class FakeTaskTable:
    """Une seule tâche en mémoire ; `script` simule l'évolution du statut entre deux lectures."""

    def __init__(self, task: TaskModel, statuses: list[str]):
        self.task = task
        self.statuses = statuses
        self.updates: list = []

    def get_task_by_id(self, task_id):
        if self.statuses:
            self.task.status = self.statuses.pop(0)
        return self.task.model_copy(deep=True)

    def update_task(self, task_id, form_data):
        self.updates.append(form_data)
        for key, value in form_data.model_dump(exclude_unset=True).items():
            if key == "output":
                value = OCRResult.model_validate(value)
            setattr(self.task, key, value)
        return self.task.model_copy(deep=True)


class FakeLayoutModel(BaseModelPrediction):
    def __init__(self, fail: bool = False, with_table: bool = False):
        super().__init__()
        self.fail = fail
        self.with_table = with_table

    def batch_predict(self, images, pages=[], *args, **kwargs):
        if self.fail:
            raise RuntimeError("model exploded")
        for page in pages:
            box = Layout(cls_id=1, label="image", score=0.9, coordinate=[0.1, 0.1, 0.5, 0.5])
            page.layouts = [box]
            page.images = [box.model_copy()]
            if self.with_table:
                page.tables = [Layout(cls_id=2, label="table", score=0.9, coordinate=[0.2, 0.2, 0.8, 0.6])]
        return pages


class FakeConnector:
    bucket_name = "bucket"

    def __init__(self, image_path):
        self.image_path = image_path
        self.deleted = []
        self.client = SimpleNamespace(delete_object=lambda Bucket, Key: self.deleted.append(Key))

    def download_by_s3_key(self, s3_key):
        return str(self.image_path)


def make_task(ocr_pages: int = 1) -> TaskModel:
    return TaskModel(
        id="t1",
        user_id="u1",
        type="default",
        status=TaskStatus.IN_PROGRESS.value,
        created_at=0,
        updated_at=0,
        extras={LAYOUT_STATUS_KEY: "pending", "keep": "me"},
        input=InputForm(
            storage_file_path="u1/t1/layout/a.png", raw_filename="a.png", content_type="image/png", ext=".png", size=1
        ),
        output=OCRResult(
            type="ocr",
            model_name="m",
            created_at=0,
            updated_at=0,
            version="1",
            total_pages=ocr_pages,
            pages=[Page(page=i) for i in range(ocr_pages)],
        ),
    )
