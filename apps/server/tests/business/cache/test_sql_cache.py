from unittest.mock import MagicMock

from business.cache.sql_cache import TaskCache
from src.schemas.input import InputForm
from src.schemas.output import OCRResult, Page
from src.schemas.task import TaskModel, TaskStatus


def _cached_task() -> TaskModel:
    return TaskModel(
        id="cached-task",
        user_id="user-1",
        type="ocr",
        status=TaskStatus.COMPLETED.value,
        percentage=1,
        input=InputForm(
            storage_file_path="user-1/cached-task/identite.jpg",
            raw_filename="identite.jpg",
            ext=".jpg",
            size=1234,
            content_type="image/jpeg",
        ),
        output=OCRResult(
            type="ocr",
            model_name="test",
            version="1",
            created_at=0,
            updated_at=0,
            total_pages=1,
            pages=[Page(page=0)],
        ),
        created_at=0,
        updated_at=0,
    )


def test_update_get_obj_reads_the_upload_from_its_stored_key():
    file_connector = MagicMock()
    file_connector.download_by_s3_key.return_value = "tests/data/valid/identite.jpg"
    file_connector.client.generate_presigned_url.return_value = "https://storage.example/page_0.jpg"
    task = _cached_task()

    result = TaskCache(file_connector=file_connector).update_get_obj(task)

    # The key carries the filename; `<user>/<task>` alone points at nothing.
    file_connector.download_by_s3_key.assert_called_once_with(s3_key="user-1/cached-task/identite.jpg")
    assert result.output.pages[0].page_url == "https://storage.example/page_0.jpg"
