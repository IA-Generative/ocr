import pytest
from PIL import Image

from services.base.model import BaseModelPrediction
from src.schemas.output import Page
from src.connector.s3_connector import S3Connector
from services.base.worker import FileNotSupported, AnyFileProcessWorker, hash_file
from src.schemas.input import InputForm
from src.schemas.task import TaskForm, TaskModel, task_table, TaskStatus
from src.schemas.output import OCRResult


class MockeBaseModelPrediction(BaseModelPrediction):
    def __init__(self):
        super().__init__()

    def batch_predict(self, images: list, pages: list[Page], *args, **kwargs) -> list[Page]:
        return [Page(page=i) for i, _ in enumerate(images)]


@pytest.fixture
def dummy_task() -> TaskModel:
    return task_table.insert_new_task(user_id="123", form_data=TaskForm(user_id="123", type="ocr", status="created"))


@pytest.fixture
def mock_minio() -> S3Connector:
    return S3Connector()


@pytest.fixture
def mock_model() -> MockeBaseModelPrediction:
    return MockeBaseModelPrediction()


def test_get_content_file_success(
    mock_minio: S3Connector, mock_model: MockeBaseModelPrediction, dummy_task: TaskModel, tmp_path
):
    expected_content = b"fake-bytes-content"
    source_path = tmp_path / "data.txt"
    source_path.write_bytes(expected_content)

    mock_minio.save(task_id=dummy_task.id, user_id=dummy_task.user_id, file_path=str(source_path))
    dummy_task.input = InputForm(
        storage_file_path=f"{dummy_task.user_id}/{dummy_task.id}/data.txt",
        raw_filename="data.txt",
        ext=".txt",
        size=len(expected_content),
        content_type="text/plain",
    )

    worker = AnyFileProcessWorker(name="test", file_connector=mock_minio, models=[mock_model])
    file_path = worker.get_content_file(task=dummy_task)
    with open(file_path, "rb") as f:
        content = f.read()

    assert content == expected_content
    mock_minio.delete_by_task_id(user_id=dummy_task.user_id, task_id=dummy_task.id)


def test_completed_task_drops_the_uploaded_file_but_keeps_the_page_images(
    mock_minio: S3Connector, mock_model: MockeBaseModelPrediction, dummy_task: TaskModel
):
    image_path = "tests/data/valid/identite.jpg"
    storage_file_path = mock_minio.save(
        user_id=dummy_task.user_id, task_id=dummy_task.id, file_path=image_path, filename="identite.jpg"
    )
    dummy_task.input = InputForm(
        storage_file_path=storage_file_path,
        raw_filename="identite.jpg",
        ext=".jpg",
        size=123456,
        content_type="image/jpg",
    )
    worker = AnyFileProcessWorker(name="test", file_connector=mock_minio, models=[mock_model])

    try:
        done = worker.process_task(task=dummy_task)

        listing = mock_minio.client.list_objects_v2(
            Bucket=mock_minio.bucket_name, Prefix=f"{dummy_task.user_id}/{dummy_task.id}/"
        )
        assert done.status == TaskStatus.COMPLETED.value
        assert [obj["Key"] for obj in listing.get("Contents", [])] == [
            f"{dummy_task.user_id}/{dummy_task.id}/images/page_0.jpg"
        ]
    finally:
        mock_minio.delete_by_task_id(user_id=dummy_task.user_id, task_id=dummy_task.id)


def test_get_content_file_exception(
    mock_minio: S3Connector, mock_model: MockeBaseModelPrediction, dummy_task: TaskModel
):
    worker = AnyFileProcessWorker(name="test", file_connector=mock_minio, models=[mock_model])

    with pytest.raises(Exception):
        worker.get_content_file(task=dummy_task)


def test_set_task_extras(mock_minio: S3Connector, mock_model: MockeBaseModelPrediction, dummy_task: TaskModel):
    worker = AnyFileProcessWorker(name="test", file_connector=mock_minio, models=[mock_model])
    actual = worker.set_extras(task=dummy_task)
    assert actual.extras is not None


def test_transform_content_error_no_content_type(
    mock_minio: S3Connector, mock_model: MockeBaseModelPrediction, dummy_task: TaskModel
):
    dummy_task.input = InputForm(
        storage_file_path="tests/data/valid/identite.jpg",
        raw_filename="identite.jpg",
        ext=".jpg",
        size=123456,
        content_type="vvv/ssjpg",
    )
    worker = AnyFileProcessWorker(name="test", file_connector=mock_minio, models=[mock_model])
    dummy_task.extras = {}
    with open("tests/data/valid/identite.jpg", "rb") as f:
        expected_content = f.read()
        with pytest.raises(FileNotSupported):
            worker.transform_content(task=dummy_task, content=expected_content)


def test_transform_content_content_type_image(
    mock_minio: S3Connector, mock_model: MockeBaseModelPrediction, dummy_task: TaskModel
):
    dummy_task.input = InputForm(
        storage_file_path="tests/data/valid/identite.jpg",
        raw_filename="identite.jpg",
        ext=".jpg",
        size=123456,
        content_type="image/jpg",  # Uncomment this line to simulate the absence of content_type
    )

    worker = AnyFileProcessWorker(name="test", file_connector=mock_minio, models=[mock_model])
    with open("tests/data/valid/identite.jpg", "rb") as f:
        actual = worker.transform_content(task=dummy_task, content=f)
        assert isinstance(actual[0], Image.Image)


def test_transform_content_content_type_pdf(
    mock_minio: S3Connector, mock_model: MockeBaseModelPrediction, dummy_task: TaskModel
):
    dummy_task.input = InputForm(
        storage_file_path="tests/data/valid/cerfa_13750-05-1.pdf",
        raw_filename="cerfa_13750-05-1.pdf",
        ext=".pdf",
        size=123456,
        content_type="application/pdf",  # Uncomment this line to simulate the absence of content_type
    )

    worker = AnyFileProcessWorker(
        name="test",
        file_connector=mock_minio,
        models=[mock_model],
    )

    actual = worker.transform_content(task=dummy_task, content="tests/data/valid/cerfa_13750-05-1.pdf")
    assert isinstance(actual[0], Image.Image)
    assert len(actual) == 1


def test_predict_on_pages(mock_minio: S3Connector, mock_model: MockeBaseModelPrediction, dummy_task: TaskModel):
    dummy_task.input = InputForm(
        storage_file_path="tests/data/valid/identite.jpg",
        raw_filename="identite.jpg",
        ext=".jpg",
        size=123456,
        content_type="image/jpg",  # Uncomment this line to simulate the absence of content_type
    )
    worker = AnyFileProcessWorker(name="test", file_connector=mock_minio, models=[mock_model])

    image = Image.open("tests/data/valid/identite.jpg")
    actual = worker.predict_on_pages(task=dummy_task, pages=[image])
    assert actual is not None


def test_predict_get_from_hash(
    mock_minio: S3Connector,
    mock_model: MockeBaseModelPrediction,
    dummy_task: TaskModel,
    monkeypatch: pytest.MonkeyPatch,
):
    from services.base.cache import BaseCache

    input = InputForm(
        storage_file_path="tests/data/valid/identite.jpg",
        raw_filename="identite.jpg",
        ext=".jpg",
        size=123456,
        content_type="image/jpg",  # Uncomment this line to simulate the absence of content_type
    )

    cache_task = TaskModel(
        id="1111",
        user_id="unk",
        type="",
        input=input,
        status=TaskStatus.COMPLETED.value,
        percentage=1,
        content_hash=hash_file(input.storage_file_path),
        output=OCRResult(
            type="mix",
            model_name="1",
            created_at=2,
            updated_at=3,
            version="1",
            total_pages=1,
            pages=[],
        ),
        created_at=0,
        updated_at=1,
    )
    monkeypatch.setattr(
        mock_minio,
        "download_by_s3_key",
        lambda *args, **kwargs: "tests/data/valid/identite.jpg",
    )

    class MockCache(BaseCache):
        def is_in_cache(self, task: TaskModel) -> bool:
            return True

        def get_task_from_cache(self, task: TaskModel) -> TaskModel:
            return cache_task

    dummy_task.input = InputForm(
        storage_file_path="tests/data/valid/identite.jpg",
        raw_filename="identite.jpg",
        ext=".jpg",
        size=123456,
        content_type="image/jpg",  # Uncomment this line to simulate the absence of content_type
    )
    mock_minio.save(
        user_id=dummy_task.user_id,
        task_id=dummy_task.id,
        file_path=dummy_task.input.storage_file_path,
    )
    worker = AnyFileProcessWorker(name="test", file_connector=mock_minio, models=[mock_model], cache=MockCache())
    update_task = worker.process_task(task=dummy_task)
    assert update_task.percentage == cache_task.percentage
    assert update_task.status == TaskStatus.COMPLETED.value
    assert update_task.output == cache_task.output


def test_worker_predict_on_pages_raise_exception(
    mock_minio: S3Connector, mock_model: MockeBaseModelPrediction, dummy_task: TaskModel
):
    class MockeExceptionWorker(AnyFileProcessWorker):
        def predict_on_pages(self, task: TaskModel, pages: list[Image.Image]) -> TaskModel:
            raise Exception("Mocked exception")

    worker = MockeExceptionWorker(name="test", file_connector=mock_minio, models=[mock_model])
    dummy_task.input = InputForm(
        storage_file_path="tests/data/valid/identite.jpg",
        raw_filename="identite.jpg",
        ext=".jpg",
        size=123456,
        content_type="image/jpg",  # Uncomment this line to simulate the absence of content_type
    )
    mock_minio.save(
        user_id=dummy_task.user_id,
        task_id=dummy_task.id,
        file_path=dummy_task.input.storage_file_path,
    )
    with pytest.raises(Exception):
        worker.process_task(task=dummy_task)


def test_raise_exception_on_retrieve_content(
    mock_minio: S3Connector, mock_model: MockeBaseModelPrediction, dummy_task: TaskModel
):
    class MockeExceptionWorker(AnyFileProcessWorker):
        def get_content_file(self, task: TaskModel) -> str:
            raise Exception("Mocked exception")

    worker = MockeExceptionWorker(name="test", file_connector=mock_minio, models=[mock_model])
    with pytest.raises(Exception):
        worker.get_content_file(task=dummy_task)


def test_base_worker_is_applicable(
    mock_minio: S3Connector, mock_model: MockeBaseModelPrediction, dummy_task: TaskModel
):
    dummy_task.input = InputForm(
        storage_file_path="tests/data/valid/identite.jpg",
        raw_filename="identite.jpg",
        ext=".jpg",
        size=123456,
        content_type="image/jpg",  # Uncomment this line to simulate the absence of content_type
    )
    worker = AnyFileProcessWorker(name="test", file_connector=mock_minio, models=[mock_model])
    assert worker.is_applicable(task=dummy_task) is True

    dummy_task.input.content_type = "image/jpg"
    assert worker.is_applicable(task=dummy_task) is True

    dummy_task.input.content_type = "application/pdf"
    assert worker.is_applicable(task=dummy_task) is True

    dummy_task.input.content_type = "text/plain"
    assert worker.is_applicable(task=dummy_task) is False
