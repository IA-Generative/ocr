import boto3
import pytest
import json

from unittest.mock import patch

from src.schemas.task import task_table, TaskForm, TaskModel, TaskStatus
from src.schemas.input import InputForm


from src.connector.base import BaseFileConnector
from src.connector.s3_connector import S3Connector
from src.config.s3 import S3Settings
from src.schemas.output import Page
from services.base.worker import AnyFileProcessWorker
from services.base.pipeline import Pipeline
from services.base.model import BaseModelPrediction


@pytest.fixture(scope="module")
def mocked_models() -> BaseModelPrediction:
    class MockeModel(BaseModelPrediction):
        def batch_predict(self, images, pages=..., *args, **kwargs):
            return [Page(page=i) for i in range(len(images))]

    return MockeModel()


@pytest.fixture(scope="module")
def storage_service() -> BaseFileConnector:
    settings = S3Settings()
    return S3Connector(s3_client=boto3.client("s3"), bucket_name=settings.AWS_BUCKET_NAME)


@pytest.fixture(scope="module")
def mocked_pipeline(storage_service: BaseFileConnector, mocked_models: BaseModelPrediction) -> Pipeline:
    return Pipeline([AnyFileProcessWorker(name="mock", file_connector=storage_service, models=[mocked_models])])


def test_task_process_paddle(storage_service: BaseFileConnector, mocked_pipeline: Pipeline):
    with patch("services.factory.load_worker", return_value=mocked_pipeline):
        from services.main import launch_task

        user_id = "test"
        task = task_table.insert_new_task(
            user_id=user_id,
            form_data=TaskForm(
                user_id=user_id,
                type="OCR",
                status=TaskStatus.CREATED.value,
                percentage=0,
                extras={},
            ),
        )

        saved_path = storage_service.save(
            user_id=user_id,
            task_id=task.id,
            file_path="tests/data/valid/cerfa_13750-05-1.pdf",
        )
        task.input = InputForm(
            type="file",
            storage_file_path=saved_path,
            raw_filename="cerfa_13750-05-1.pdf",
            content_type="application/pdf",
            ext=".pdf",
            size=123456,
        )
        result = launch_task.apply(args=(json.dumps(task.model_dump()),))
        result = result.get()
        actual = TaskModel.model_validate(result)
        assert actual.id == task.id
        assert actual.status == TaskStatus.COMPLETED.value


def test_failed_task_keeps_its_error_but_not_the_stack_trace():
    import services.main as worker_main

    class FailingPipeline:
        def process(self, task):
            raise RuntimeError("model exploded")

    task = task_table.insert_new_task(
        user_id="test",
        form_data=TaskForm(user_id="test", type="OCR", status=TaskStatus.QUEUED.value, percentage=0, extras={}),
    )

    with patch.object(worker_main, "process_ocr", FailingPipeline()):
        with pytest.raises(RuntimeError, match="model exploded"):
            worker_main._run_task(task)

    stored = task_table.get_task_by_id(task.id)
    assert stored.status == TaskStatus.FAILED.value
    assert stored.extras["error"] == "model exploded"
    # `extras` is part of the task returned by the API.
    assert "traceback" not in stored.extras
