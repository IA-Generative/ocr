import os
import tempfile
import boto3
import pytest
from src.connector.s3_connector import S3Connector
from src.config.s3 import S3Settings
from botocore.client import Config

settings = S3Settings()


@pytest.fixture(scope="module")
def s3_client():
    return boto3.client(
        "s3",
        config=Config(signature_version="s3v4"),
    )


@pytest.fixture(scope="module")
def s3_connector(s3_client):
    bucket_name = settings.AWS_BUCKET_NAME
    connector = S3Connector(s3_client, bucket_name)
    return connector


def test_save_and_get_file(s3_connector: S3Connector):
    user_id = "user123"
    task_id = "task456"

    with tempfile.NamedTemporaryFile("w+b", delete=False) as tmp:
        tmp.write(b"Hello World!")
        tmp_path = tmp.name

    try:
        object_key = s3_connector.save(user_id, task_id, tmp_path)
        assert object_key == f"{user_id}/{task_id}/{os.path.basename(tmp_path)}"

        file_data = s3_connector.download_by_s3_key(object_key)
        with open(file_data, "rb") as f:
            assert f.read() == b"Hello World!"
    finally:
        os.remove(tmp_path)


def _stored_keys(s3_connector: S3Connector, prefix: str) -> list[str]:
    response = s3_connector.client.list_objects_v2(Bucket=s3_connector.bucket_name, Prefix=prefix)
    return sorted(obj["Key"] for obj in response.get("Contents", []))


def _store(s3_connector: S3Connector, key: str) -> None:
    s3_connector.client.put_object(Bucket=s3_connector.bucket_name, Key=key, Body=b"content")


def test_delete_by_task_id_removes_the_upload_and_the_page_images(s3_connector: S3Connector):
    user_id = "user-delete-by-task"
    with tempfile.NamedTemporaryFile("w+b", delete=False, suffix=".pdf") as tmp:
        tmp.write(b"Hello World!")
        tmp_path = tmp.name
    try:
        upload_key = s3_connector.save(user_id, "task-a", tmp_path, "scan.pdf")
    finally:
        os.remove(tmp_path)
    _store(s3_connector, f"{user_id}/task-a/images/page_0.jpg")
    _store(s3_connector, f"{user_id}/task-a/images/page_1.jpg")
    # Neighbours that must survive: another task of the same user, and a task whose id
    # merely starts with the deleted one's.
    _store(s3_connector, f"{user_id}/task-b/scan.pdf")
    _store(s3_connector, f"{user_id}/task-a2/scan.pdf")
    assert upload_key in _stored_keys(s3_connector, f"{user_id}/task-a/")

    try:
        assert s3_connector.delete_by_task_id(user_id, "task-a") is True

        assert _stored_keys(s3_connector, f"{user_id}/") == [
            f"{user_id}/task-a2/scan.pdf",
            f"{user_id}/task-b/scan.pdf",
        ]
    finally:
        s3_connector.delete_by_user_id(user_id)


def test_delete_by_task_id_is_a_noop_for_an_unknown_task(s3_connector: S3Connector):
    assert s3_connector.delete_by_task_id("user-without-tasks", "unknown-task") is True


def test_delete_by_s3_key_removes_only_that_object(s3_connector: S3Connector):
    user_id = "user-delete-by-key"
    _store(s3_connector, f"{user_id}/task-a/scan.pdf")
    _store(s3_connector, f"{user_id}/task-a/images/page_0.jpg")

    try:
        assert s3_connector.delete_by_s3_key(f"{user_id}/task-a/scan.pdf") is True

        assert _stored_keys(s3_connector, f"{user_id}/") == [f"{user_id}/task-a/images/page_0.jpg"]
    finally:
        s3_connector.delete_by_user_id(user_id)


def test_delete_by_user_id(s3_connector: S3Connector):
    user_id = "user_to_delete"
    for i in range(3):
        with tempfile.NamedTemporaryFile("w+b", delete=False) as tmp:
            tmp.write(f"File {i}".encode())
            tmp_path = tmp.name
        try:
            s3_connector.save(user_id, f"task_{i}", tmp_path)
        finally:
            os.remove(tmp_path)

    success = s3_connector.delete_by_user_id(user_id)
    assert success
