from PIL import Image
import time
from io import BytesIO
from services.base.cache import BaseCache
from src.schemas.task import TaskModel, task_table, TaskStatus
from src.connector.s3_connector import S3Connector
from services.utils.lazy_pdf import LazyPdfImageList
from src.logger import logger
import os

# logger.setLevel(logging.DEBUG)
USE_CACHE = os.getenv("USE_CACHE", "false").lower() == "true"


class TaskCache(BaseCache):
    def __init__(self, file_connector: S3Connector):
        self.file_connector = file_connector

    def is_in_cache(self, task: TaskModel) -> bool:
        if not USE_CACHE:
            return False
        found_task = task_table.get_task_by_content_hash(content_hash_value=task.content_hash)
        return (
            found_task is not None and found_task.status == TaskStatus.COMPLETED.value and found_task.type == task.type
        )

    def update_get_obj(self, task: TaskModel) -> TaskModel:
        if not self.file_connector:
            return task
        filename = task.input.raw_filename
        content_type = task.input.content_type
        content = self.file_connector.download_by_s3_key(s3_key=task.input.storage_file_path)

        if content_type.startswith("image/"):
            images = [Image.open(content).convert("RGB")]

        elif content_type == "application/pdf":
            t_convert = time.time()
            logger.debug(f"{task.id} - {filename} convert to image")
            logger.info(79 * "*")

            images = LazyPdfImageList(content)
            t_convert = time.time() - t_convert
            logger.debug(f"{task.id} - {filename} convert to image nb pages {len(images)} into {t_convert}")

        else:
            logger.error(f"Unsupported file type {task.extras}")
            task.extras["error"] = f"Unsupported file type {task.extras}"
            raise NotImplementedError(f"Unsupported file type {task.extras}")
        index = 0
        for page, image in zip(task.output.pages, images):
            buffer = BytesIO()
            image.save(buffer, format="JPEG")
            buffer.seek(0)
            key = f"{task.user_id}/{task.id}/images/page_{index}.jpg"
            self.file_connector.client.upload_fileobj(buffer, self.file_connector.bucket_name, key)
            logger.debug(f"Uploaded page {index} to {key}")
            signed_url = self.file_connector.client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": self.file_connector.bucket_name, "Key": key},
                ExpiresIn=3600,  # 1h
            )
            page.page_url = signed_url
            index += 1

        return task

    def get_task_from_cache(self, task: TaskModel) -> TaskModel:
        task_found = task_table.get_task_by_content_hash(content_hash_value=task.content_hash)
        if task_found:
            task_found.input = task.input
            task_found.id = task.id
            task_found.user_id = task.user_id
            task_found = self.update_get_obj(task=task_found)

        return task_found
