import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from ocr_backend.main import app
from src.schemas.task import TaskStatus
from ocr_backend.core.security.token import RequestContext


@pytest.fixture()
def client():
    client = TestClient(app)
    return client


@pytest.fixture
def mock_request_context():
    return RequestContext(user_id="test_user", is_admin=False)


def test_process_route_exists(client):
    response = client.put("/api/process")
    assert response.status_code != 404


@patch("ocr_backend.routers.process.TokenVerifier")
@patch("ocr_backend.routers.process.upload_file")
@patch("ocr_backend.routers.process.get_task_by_id_user")
def test_process_document_success(mock_get_task, mock_upload_file, mock_token_verifier, client):
    # Arrange
    mock_token_verifier.return_value = RequestContext(user_id="test_user", is_admin=False)

    # Mock task result
    mock_task_result = MagicMock()
    mock_task_result.id = "task_123"
    mock_upload_file.return_value = mock_task_result

    # Mock completed task with OCR results
    mock_completed_task = MagicMock()
    mock_completed_task.id = "task_123"
    mock_completed_task.status = TaskStatus.COMPLETED.value
    mock_completed_task.output = MagicMock()
    mock_completed_task.output.pages = [MagicMock()]
    mock_completed_task.output.set_page_text.return_value = "Extracted text content"

    mock_get_task.return_value = mock_completed_task

    # Test data
    test_data = b"fake pdf content"
    headers = {
        "x-filename": "test.pdf",
        "content-type": "application/pdf",
        "authorization": "Bearer fake_token",
    }

    # Act
    response = client.put("/api/process", content=test_data, headers=headers)

    # Assert
    assert response.status_code == 200, response.text
    result = response.json()
    assert len(result) == 1
    assert result[0]["page_content"] == "Extracted text content"
    assert result[0]["metadata"]["filename"] == "test.pdf"
    assert result[0]["metadata"]["mime_type"] == "application/pdf"
    assert result[0]["metadata"]["task_id"] == "task_123"


@patch("ocr_backend.routers.process.TokenVerifier")
@patch("ocr_backend.routers.process.upload_file")
@patch("ocr_backend.routers.process.get_task_by_id_user")
def test_process_document_failed_task(mock_get_task, mock_upload_file, mock_token_verifier, client):
    # Arrange
    mock_token_verifier.return_value = RequestContext(user_id="test_user", is_admin=False)

    mock_task_result = MagicMock()
    mock_task_result.id = "task_123"
    mock_upload_file.return_value = mock_task_result

    # Mock failed task
    mock_failed_task = MagicMock()
    mock_failed_task.id = "task_123"
    mock_failed_task.status = TaskStatus.FAILED.value
    mock_failed_task.extras = {"error": "OCR processing error"}

    mock_get_task.return_value = mock_failed_task

    test_data = b"fake pdf content"
    headers = {
        "x-filename": "test.pdf",
        "content-type": "application/pdf",
        "authorization": "Bearer fake_token",
    }

    # Act
    response = client.put("/api/process", content=test_data, headers=headers)

    # Assert
    assert response.status_code == 500
    assert "OCR processing failed: OCR processing error" in response.json()["detail"]


@patch("ocr_backend.routers.process.TokenVerifier")
def test_process_document_empty_body(mock_token_verifier, client):
    # Arrange
    mock_token_verifier.return_value = RequestContext(user_id="test_user", is_admin=False)

    headers = {"authorization": "Bearer fake_token"}

    # Act
    response = client.put("/api/process", content=b"", headers=headers)

    # Assert
    assert response.status_code == 400
    assert "Empty file data" in response.json()["detail"]


@patch("ocr_backend.routers.process.TokenVerifier")
@patch("ocr_backend.routers.process.upload_file")
@patch("ocr_backend.routers.process.get_task_by_id_user")
def test_process_document_no_text_extracted(mock_get_task, mock_upload_file, mock_token_verifier, client):
    # Arrange
    mock_token_verifier.return_value = RequestContext(user_id="test_user", is_admin=False)

    mock_task_result = MagicMock()
    mock_task_result.id = "task_123"
    mock_upload_file.return_value = mock_task_result

    # Mock completed task without OCR results
    mock_completed_task = MagicMock()
    mock_completed_task.id = "task_123"
    mock_completed_task.status = TaskStatus.COMPLETED.value
    mock_completed_task.output = None

    mock_get_task.return_value = mock_completed_task

    test_data = b"fake image content"
    headers = {
        "x-filename": "test.jpg",
        "content-type": "image/jpeg",
        "authorization": "Bearer fake_token",
    }

    # Act
    response = client.put("/api/process", content=test_data, headers=headers)

    # Assert
    assert response.status_code == 200, response.text
    result = response.json()
    assert len(result) == 1
    assert "aucun texte n'a été extrait" in result[0]["page_content"]
    assert result[0]["metadata"]["filename"] == "test.jpg"


@patch("ocr_backend.routers.process.TokenVerifier")
def test_process_document_default_headers(mock_token_verifier, client):
    # Arrange
    mock_token_verifier.return_value = RequestContext(user_id="test_user", is_admin=False)

    headers = {"authorization": "Bearer fake_token"}

    # Act
    response = client.put("/api/process", content=b"", headers=headers)

    # Assert - Should fail on empty body, but headers should be handled
    assert response.status_code == 400


@patch("ocr_backend.routers.process.TokenVerifier")
@patch("ocr_backend.routers.process.upload_file")
def test_process_document_upload_file_exception(mock_upload_file, mock_token_verifier, client):
    # Arrange
    mock_token_verifier.return_value = RequestContext(user_id="test_user", is_admin=False)
    mock_upload_file.side_effect = Exception("Upload failed")

    test_data = b"fake pdf content"
    headers = {
        "x-filename": "test.pdf",
        "content-type": "application/pdf",
        "authorization": "Bearer fake_token",
    }

    # Act
    response = client.put("/api/process", content=test_data, headers=headers)

    # Assert
    assert response.status_code == 500
    assert "Internal server error" in response.json()["detail"]


@pytest.mark.parametrize("route", ["/api/process", "/api/v1/openwebui/process"])
@pytest.mark.parametrize("header", ["poll-interval", "max-wait-time"])
@pytest.mark.parametrize("value", ["0", "-1"])
def test_process_routes_reject_non_positive_wait_headers(client, route, header, value):
    # A poll interval of 0 (or less) never advances the wait counter, so the request would
    # poll the database in a tight loop for as long as the task stays unfinished.
    response = client.put(route, content=b"fake pdf content", headers={header: value})

    assert response.status_code == 422, response.text
