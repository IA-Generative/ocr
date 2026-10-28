import pymupdf
import io
from time import time
import tempfile
from abc import abstractmethod, ABC
from PIL import Image
from services.base.model import BaseModelPrediction
from src.schemas.output import Page
from src.schemas.box import Bbox
from src.schemas.vector import Vector
from src.logger import logger, Colors
from src.connector.collection_manager import QdrantVectorStore
from src.schemas.task import TaskModel
from src.schemas.input import RegionOfInterest
from src.schemas.templates import template_table, TemplateForm
from src.connector.s3_connector import S3Connector
from src.utils.file import hash_file
from uuid import uuid4


class FeatureCreator(BaseModelPrediction, ABC):
    def __init__(
        self,
        model_name: str = "feature_creator",
        model_size: int = 128,
        **kwargs,
    ):
        super().__init__()
        self.model_name = model_name
        self.model_size = model_size
        logger.info(f"Initialized FeatureCreator with model {self.model_name} and size {self.model_size}")

    @abstractmethod
    def get_vector_from_image(self, image: Image.Image) -> list[float]: ...

    def batch_predict(self, images: list[Image.Image], pages: list[Page] = [], *args, **kwargs):
        assert len(pages) == len(images), "Not the same lenght"
        init_t = time()
        for image, page in zip(images, pages):
            t = time()
            vector = self.get_vector_from_image(image)
            page.vector = Vector(
                model_name=self.model_name,
                vector=vector,
                vector_size=len(vector),
                collection_name=self.current_task.group_id,
                label=f"page-{page.page}-feature",
                id=str(uuid4()),
                source_id=self.current_task.id,
                page_num=page.page,
            )

            logger.debug(
                f"[{self.__class__.__name__}]: Time to create feature vector for page {page.page}: {time() - t:.2f}s"
            )
        logger.debug(
            f"[{self.__class__.__name__}]: Total time to create feature vectors for {len(pages)} pages: {time() - init_t:.2f}s"
        )
        return pages


class DummyFeatureCreator(FeatureCreator):
    def __init__(self, model_name: str = "dummy-feature", model_size: int = 128, **kwargs):
        super().__init__(model_name=model_name, model_size=model_size, **kwargs)

    def get_vector_from_image(self, image: Image.Image) -> list[float]:
        # Dummy vector generation logic
        return [0.0] * self.model_size


class FeatureSaver(BaseModelPrediction):
    def __init__(
        self,
        collection_manager: QdrantVectorStore,
        file_connector: S3Connector,
        **kwargs,
    ):
        super().__init__()
        self.collection_manager = collection_manager
        self.file_connector = file_connector
        self.current_task: TaskModel | None = None

    def set_interest_zone(self, task: TaskModel):
        if task.input is None:
            raise ValueError("Task input is required to set interest zone.")
        if task.input.content_type.startswith("image/"):
            self._handle_image_interest_zone(task)
        elif task.input.content_type == "application/pdf":
            self._handle_pdf_interest_zone(task)
        return task

    def _handle_image_interest_zone(self, task: TaskModel):
        if task.input.interest_zone is None:
            raise ValueError("Interest zone is required for image tasks but not provided.")
        if len(task.input.interest_zone) != 1:
            raise ValueError("Interest zone must contain exactly one entry for image tasks.")

    def _handle_pdf_interest_zone(self, task: TaskModel):
        doc: pymupdf.Document = pymupdf.open(self.file_connector.get_by_task_id(user_id=task.user_id, task_id=task.id))
        logger.debug(
            f"{Colors.YELLOW}[{self.__class__.__name__}]: Processing PDF with {len(doc)} pages for task {task.id} - is form: {doc.is_form_pdf} - interest zone: {len(task.input.interest_zone)} {Colors.RESET}"
        )
        if not doc.is_form_pdf or task.input.interest_zone:
            assert len(task.input.interest_zone) == len(doc), (
                f"{Colors.RED}Interest zone length must match the number of pages in the PDF.{Colors.RESET}"
            )
        else:
            task.input.interest_zone = []
            dpi = 150
            scale = dpi / 72
            for i in range(len(doc)):
                page = doc[i]
                pix = page.get_pixmap(dpi=dpi)
                img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
                region = RegionOfInterest(labels=f"Page-{i + 1:05}-{task.input.raw_filename}", page=i)
                for widget in page.widgets():
                    region.interest_zone.append(self._create_bbox_from_widget(widget, img, scale))
                task.input.interest_zone.append(region)
            logger.debug(
                f"{Colors.YELLOW}[{self.__class__.__name__}][{task.id}]: Created interest zones for {len(task.input.interest_zone)} pages in the PDF.{Colors.RESET}"
            )

    def _create_bbox_from_widget(self, widget: pymupdf.Widget, img: Image.Image, scale: float) -> Bbox:
        rect = widget.rect
        name = widget.field_name
        value = widget.field_value

        x0, y0 = (
            rect.x0 * scale / img.width,
            rect.y0 * scale / img.height,
        )
        x1, y1 = (
            rect.x1 * scale / img.width,
            rect.y1 * scale / img.height,
        )

        return Bbox(
            x=x0,
            y=y0,
            width=x1 - x0,
            height=y1 - y0,
            confidence=1.0,
            text=f"{name} = {value}",
        )

    def set_current_task(self, task):
        task = self.set_interest_zone(task)
        return super().set_current_task(task)

    def batch_predict(self, images: list[Image.Image], pages: list[Page] = [], *args, **kwargs) -> list[Page]:
        assert len(pages) == len(images), "Not the same lenght"
        if not self.current_task:
            raise ValueError("Source task not found in database.")

        if not self.collection_manager.collection_exists(collection_name=self.current_task.group_id):
            raise ValueError(
                f"{Colors.RED}Collection {self.current_task.group_id} does not exist in the vector store.{Colors.RESET}"
            )

        logger.debug(f"[{self.__class__.__name__}]: Saving templates for task {self.current_task.id}")
        indices_interest_zone = [page.page for page in pages]
        logger.debug(
            f"[{self.__class__.__name__}]: Indices of interest zone: {len(indices_interest_zone)} {indices_interest_zone} images : {len(images)}"
        )
        current_interest_zone: list[RegionOfInterest] = []
        for i in indices_interest_zone:
            current_interest_zone.append(self.current_task.input.interest_zone[i])

        t = time()
        for page, image, interest_zone in zip(pages, images, current_interest_zone):
            # save image to s3
            # Get the hash of the image to use as the ID
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                filename = temp_file.name + ".jpg"
                image.save(filename, format="JPEG")
                temp_file.flush()
                # Save the image to S3
                save_path = self.file_connector.save(
                    user_id=self.current_task.group_id,
                    task_id=hash_file(filename),
                    file_path=filename,
                )
            if (
                page.vector is None
                or page.vector.vector is None
                or self.current_task.input is None
                or self.current_task.group_id is None
            ):
                raise ValueError(f"Page {page.page} does not have a vector. Ensure the feature extractor has been run.")
            template = template_table.insert_new_template(
                TemplateForm(
                    user_id=self.current_task.user_id,
                    group_id=self.current_task.group_id,
                    description=self.current_task.input.raw_filename,
                    source_file=save_path,
                    source_task_id=self.current_task.id,
                    page_number=page.page,
                    vector=page.vector.vector,
                    vector_size=page.vector.vector_size,
                    model_name=page.vector.model_name,
                    interest_zone=interest_zone,
                )
            )

            self.collection_manager.upsert_point(
                collection_name=self.current_task.group_id,
                vector=page.vector.vector,
                point_id=template.id,
                payload=template.model_dump(exclude_none=True),
            )
            page.vector.source_id = self.current_task.id
            page.vector.id = template.id
            page.vector.collection_name = self.current_task.group_id
            page.boxes = interest_zone.interest_zone

        logger.debug(
            f"[{self.__class__.__name__}]: Time to create dummy vectors for {len(pages)} pages: {time() - t:.2f}s"
        )

        return pages


class QueryFeature(BaseModelPrediction):
    def __init__(self, collection_manager: QdrantVectorStore, **kwargs):
        super().__init__()
        self.collection_manager = collection_manager
        logger.info("Initialized Query with collection manager")

    def batch_predict(self, images: list[Image.Image], pages: list[Page], *args, **kwargs) -> list[Vector]:
        for page in pages:
            page = self._process_page(page)

        return pages

    def _process_page(self, page: Page) -> Page:
        if not self.collection_manager.collection_exists(collection_name=self.current_task.group_id):
            raise ValueError(
                f"{Colors.RED}Collection {self.current_task.group_id} does not exist in the vector store.{Colors.RESET}"
            )
        if page.vector is None or page.vector.vector is None:
            raise ValueError(f"Page {page.page} does not have a vector. Ensure the feature extractor has been run.")
        result = self.collection_manager.search_vectors(
            collection_name=self.current_task.group_id,
            query_vector=page.vector.vector,
            limit=1,
        )
        logger.debug(
            f"{Colors.BLUE}[{self.__class__.__name__}]: Found {len(result)} similar templates for page {page.page} in group {self.current_task.group_id}{Colors.RESET}"
        )
        for res in result:
            page.similar_template_ids.append((res.id, res.score))
        return page
