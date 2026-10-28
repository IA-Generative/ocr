import pytest
from unittest.mock import MagicMock, patch
from business.features.models.features_extraction import (
    DummyFeatureCreator,
    FeatureSaver,
    QueryFeature,
)
from src.schemas.output import Page
from src.schemas.box import Bbox
from src.schemas.vector import Vector
from src.schemas.input import RegionOfInterest
from PIL import Image
from qdrant_client import QdrantClient
from src.connector.s3_connector import S3Connector, BaseFileConnector
import boto3
from src.config.s3 import S3Settings
from src.connector.collection_manager import QdrantVectorStore, DistanceMetric
from src.schemas.task import TaskModel, InputForm, TaskOperation
from services.utils.lazy_pdf import LazyPdfImageList


@pytest.fixture(scope="function")
def mock_qdrant_client() -> QdrantClient:
    """Mock du client Qdrant"""
    return QdrantClient(":memory:")


@pytest.fixture(scope="module")
def storage_service() -> BaseFileConnector:
    settings = S3Settings()
    return S3Connector(s3_client=boto3.client("s3"), bucket_name=settings.AWS_BUCKET_NAME)


@pytest.fixture
def qdrant_store(mock_qdrant_client: QdrantClient) -> QdrantVectorStore:
    """Instance QdrantVectorStore avec mock client"""
    return QdrantVectorStore(mock_qdrant_client)


def test_dummy_feature_creator():
    feature_creator = DummyFeatureCreator(
        model_name="dummy",
        model_size=128,
    )

    # Create a list of dummy images (as PIL Image objects)
    images = [MagicMock(spec=Image.Image) for _ in range(5)]
    mock_task = TaskModel(
        id="test_task",
        user_id="test_user",
        input=InputForm(
            storage_file_path="tests/data/valid/cerfa_13750-05-1.pdf",
            raw_filename="test_file",
            content_type="application/pdf",
            ext=".pdf",
            size=12345,
            interest_zone=[],
        ),
        group_id="dummy_collection",
        type=TaskOperation.SAVE_TEMPLATE.value,
        status="created",
        created_at=1633036800,
        updated_at=1633036800,
    )
    feature_creator.set_current_task(mock_task)

    # Call the batch_predict method
    pages = feature_creator.batch_predict(
        images,
        pages=[Page(page=i) for i in range(len(images))],
    )

    # Check that the number of pages returned matches the number of images
    assert len(pages) == len(images)

    # Check that each page has a vector with the correct properties
    for page in pages:
        assert isinstance(page.vector, Vector)
        assert page.vector.model_name == "dummy"
        assert len(page.vector.vector) == 128
        assert page.vector.vector_size == 128

    with pytest.raises(AssertionError):
        # This should raise an error because the lengths do not match
        feature_creator.batch_predict(images, pages=[MagicMock(spec=Page) for _ in range(3)])


@patch("src.schemas.task.task_table.get_task_by_id")
def test_feature_saver(
    mock_get_task_by_id: MagicMock,  # Mock the task retrieval
    qdrant_store: QdrantVectorStore,
    storage_service: BaseFileConnector,
    monkeypatch: pytest.MonkeyPatch,
):
    # The task's input points at a local sample instead of an uploaded object.
    monkeypatch.setattr(
        storage_service, "download_by_s3_key", lambda *args, **kwargs: "tests/data/valid/cerfa_13750-05-1.pdf"
    )
    mock_task = TaskModel(
        id="test_task",
        user_id="test_user",
        input=InputForm(
            storage_file_path="tests/data/valid/cerfa_13750-05-1.pdf",
            raw_filename="test_file",
            content_type="application/pdf",
            ext=".pdf",
            size=12345,
            interest_zone=[],
        ),
        group_id="dummy_collection",
        type=TaskOperation.SAVE_TEMPLATE.value,
        status="created",
        created_at=1633036800,
        updated_at=1633036800,
    )
    mock_get_task_by_id.return_value = mock_task

    feature_saver = FeatureSaver(
        collection_manager=qdrant_store,
        file_connector=storage_service,
    )
    qdrant_store.create_collection(
        collection_name=mock_task.group_id,
        vector_size=128,
        distance=DistanceMetric.COSINE,
    )

    # Create a dummy page with a vector
    page = Page(
        page=0,
        # source_id="test_source",
        vector=Vector(
            model_name="dummy",
            vector=[0.1] * 128,
            vector_size=128,
            collection_name="test_collection",
            label="test_label",
            id="test_id",
        ),
    )
    storage_service.save(
        user_id=mock_task.user_id,
        task_id=mock_task.id,
        file_path="tests/data/valid/cerfa_13750-05-1.pdf",
    )

    feature_saver.set_current_task(task=mock_task)
    # Call the save method
    saved_pages = feature_saver.batch_predict(
        images=LazyPdfImageList("tests/data/valid/cerfa_13750-05-1.pdf"), pages=[page]
    )

    # Check that the saved page has the correct properties
    for saved_page in saved_pages:
        assert saved_page.vector.model_name == "dummy"
        assert len(saved_page.vector.vector) == 128
        assert saved_page.vector.vector_size == 128

    with pytest.raises(ValueError):
        feature_saver.current_task = None
        feature_saver.batch_predict(
            images=LazyPdfImageList("tests/data/valid/cerfa_13750-05-1.pdf"),
            pages=[page],
        )

    with pytest.raises(ValueError):
        copy_task = mock_task.model_copy()
        copy_page = page.model_copy()
        copy_page.vector = None
        feature_saver.set_current_task(copy_task)
        feature_saver.batch_predict(
            images=LazyPdfImageList("tests/data/valid/cerfa_13750-05-1.pdf"),
            pages=[copy_page],
        )

    with pytest.raises(AssertionError):
        copy_task = mock_task.model_copy()
        copy_task.input.interest_zone = [
            RegionOfInterest(bbox=Bbox(x=0, y=0, width=100, height=100, confidence=1, text="Test")),
            RegionOfInterest(bbox=Bbox(x=0, y=0, width=100, height=100, confidence=1, text="Test")),
        ]
        feature_saver.set_current_task(copy_task)
        feature_saver.batch_predict(
            images=LazyPdfImageList("tests/data/valid/cerfa_13750-05-1.pdf"),
            pages=[page],
        )


@patch("src.schemas.task.task_table.get_task_by_id")
def test_feature_saver_set_interest_zone(
    mock_get_task_by_id: MagicMock,  # Mock the task retrieval
    qdrant_store: QdrantVectorStore,
    storage_service: BaseFileConnector,
):
    mock_input = InputForm(
        storage_file_path="tests/data/valid/cerfa_13750-05-1.pdf",
        raw_filename="test_file",
        content_type="application/pdf",
        ext=".pdf",
        size=12345,
        interest_zone=None,
    )
    mock_task = TaskModel(
        id="test_task",
        user_id="test_user",
        input=mock_input,
        group_id="dummy_collection",
        type=TaskOperation.SAVE_TEMPLATE.value,
        status="created",
        created_at=1633036800,
        updated_at=1633036800,
    )
    mock_get_task_by_id.return_value = mock_task
    feature_saver = FeatureSaver(
        collection_manager=qdrant_store,
        file_connector=storage_service,
    )
    # Check that the input is set correctly
    with pytest.raises(ValueError):
        # This should raise an error because the task is not set
        mock_task.input = None
        feature_saver.set_interest_zone(mock_task)
    # Check if image and interest zone lengths match
    with pytest.raises(ValueError):
        # This should raise an error because the lengths do not match
        mock_task.input = mock_input
        mock_task.input.interest_zone = None
        mock_task.input.content_type = "image/png"
        feature_saver.set_interest_zone(mock_task)

    with pytest.raises(ValueError):
        # This should raise an error because the lengths do not match
        mock_task.input = mock_input
        mock_task.input.interest_zone = [
            RegionOfInterest(bbox=Bbox(x=0, y=0, width=100, height=100, confidence=1, text="Test")),
            RegionOfInterest(bbox=Bbox(x=0, y=0, width=100, height=100, confidence=1, text="Test")),
        ]
        mock_task.input.content_type = "image/png"
        feature_saver.set_interest_zone(mock_task)


@patch("src.schemas.task.task_table.get_task_by_id")
def test_feature_saver_set_interest_zone_reads_the_pdf_from_its_stored_key(
    mock_get_task_by_id: MagicMock,
    qdrant_store: QdrantVectorStore,
):
    file_connector = MagicMock()
    file_connector.download_by_s3_key.return_value = "tests/data/valid/cerfa_13750-05-1.pdf"
    task = TaskModel(
        id="pdf_task",
        user_id="test_user",
        input=InputForm(
            storage_file_path="test_user/pdf_task/cerfa_13750-05-1.pdf",
            raw_filename="cerfa_13750-05-1.pdf",
            content_type="application/pdf",
            ext=".pdf",
            size=12345,
            interest_zone=[],
        ),
        group_id="dummy_collection",
        type=TaskOperation.SAVE_TEMPLATE.value,
        status="created",
        created_at=1633036800,
        updated_at=1633036800,
    )
    feature_saver = FeatureSaver(collection_manager=qdrant_store, file_connector=file_connector)

    feature_saver.set_interest_zone(task)

    # The key carries the filename; `<user>/<task>` alone points at nothing.
    file_connector.download_by_s3_key.assert_called_once_with(s3_key="test_user/pdf_task/cerfa_13750-05-1.pdf")


@patch("src.schemas.task.task_table.get_task_by_id")
def test_query_feature(qdrant_store: QdrantVectorStore):
    from src.schemas.vector import VectorSearchResult

    mock_task = TaskModel(
        id="test_task",
        user_id="test_user",
        input=InputForm(
            storage_file_path="tests/data/valid/cerfa_13750-05-1.pdf",
            raw_filename="test_file",
            content_type="application/pdf",
            ext=".pdf",
            size=12345,
            interest_zone=[],
        ),
        group_id="dummy_collection",
        type=TaskOperation.SAVE_TEMPLATE.value,
        status="created",
        created_at=1633036800,
        updated_at=1633036800,
    )

    query_feature = QueryFeature(collection_manager=qdrant_store)
    # Create a dummy page with a vector
    page = Page(
        page=1,
        # source_id="test_source",
        vector=Vector(
            model_name="dummy",
            vector=[0.1] * 128,
            vector_size=128,
            collection_name="test_collection",
            label="test_label",
            id="test_id",
        ),
    )

    mock_search_vectors = [
        VectorSearchResult(
            id="page.id",
            score=0.9,
            vector=page.vector.vector,
            page_num=page.page,
            source_id=mock_task.id,
            group_id=mock_task.group_id,
        )
    ]
    query_feature.set_current_task(task=mock_task)

    # Call the save method
    with patch.object(qdrant_store, "search_vectors", return_value=mock_search_vectors) as mock_search:
        # Call the batch_predict method
        query_feature.batch_predict(images=[MagicMock(spec=Image.Image)], pages=[page])
        mock_search.assert_called()
