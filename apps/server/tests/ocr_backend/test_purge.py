from datetime import datetime, timedelta
from unittest.mock import patch

from src.connector.s3_connector import S3Connector
from src.schemas.task import TaskModel, TaskStatus, TaskTable

from ocr_backend.purge import PURGEABLE_STATUSES, purge_old_tasks


def _make_task(task_id: str, status: str) -> TaskModel:
    now = int(datetime.now().timestamp())
    return TaskModel(
        id=task_id,
        user_id="user1",
        type="ocr",
        status=status,
        percentage=100.0,
        created_at=now,
        updated_at=now,
    )


def test_purge_old_tasks_deletes_db_rows_and_s3_files():
    deleted_tasks = [_make_task("task-1", TaskStatus.COMPLETED.value), _make_task("task-2", TaskStatus.FAILED.value)]

    with (
        patch.object(TaskTable, "delete_tasks_created_before", return_value=deleted_tasks) as mock_delete,
        patch.object(S3Connector, "delete_by_task_id", return_value=True) as mock_s3_delete,
    ):
        result = purge_old_tasks()

    assert result == 2
    mock_delete.assert_called_once()
    call_kwargs = mock_delete.call_args.kwargs
    assert set(call_kwargs["statuses"]) == set(PURGEABLE_STATUSES)
    assert mock_s3_delete.call_count == 2
    mock_s3_delete.assert_any_call(user_id="user1", task_id="task-1")
    mock_s3_delete.assert_any_call(user_id="user1", task_id="task-2")


def test_purge_old_tasks_survives_s3_deletion_error():
    deleted_tasks = [_make_task("task-1", TaskStatus.COMPLETED.value)]

    with (
        patch.object(TaskTable, "delete_tasks_created_before", return_value=deleted_tasks),
        patch.object(S3Connector, "delete_by_task_id", side_effect=Exception("boom")),
    ):
        # A failed S3 cleanup must not blow up the whole purge run: the DB row is
        # already gone by this point, and the next run's S3 ListObjects-based cleanup
        # (if any) is a separate concern from this task's return value/exit status.
        result = purge_old_tasks()

    assert result == 1


def test_purge_old_tasks_uses_retention_days_from_settings():
    with (
        patch.object(TaskTable, "delete_tasks_created_before", return_value=[]) as mock_delete,
        patch("ocr_backend.purge.purge_settings") as mock_settings,
    ):
        mock_settings.TASK_RETENTION_DAYS = 30
        mock_settings.PURGE_BATCH_SIZE = 50

        purge_old_tasks()

    call_kwargs = mock_delete.call_args.kwargs
    cutoff = call_kwargs["cutoff_date"]
    expected_cutoff = datetime.now() - timedelta(days=30)
    assert abs((cutoff - expected_cutoff).total_seconds()) < 5
    assert call_kwargs["batch_size"] == 50


def test_beat_process_consumes_a_queue_the_ocr_workers_do_not_share():
    import importlib

    from src.connector.broker_connector import celery_app

    from ocr_backend import celery_beat

    original_queue = celery_app.conf.task_default_queue
    try:
        importlib.reload(celery_beat)

        # The OCR workers and the API publish to Celery's default queue ("celery"); a beat
        # worker sharing it would drop their jobs as unregistered tasks.
        assert celery_app.conf.task_default_queue == celery_beat.PURGE_QUEUE
        assert celery_beat.PURGE_QUEUE != "celery"
    finally:
        celery_app.conf.task_default_queue = original_queue
