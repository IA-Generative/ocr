import tempfile
import datetime

import boto3
from botocore.exceptions import ClientError

from ..config.s3 import S3Settings
from ..schemas.health import Health
from .base import BaseFileConnector
from ..logger import logger
import os


from boto3.s3.transfer import TransferConfig

config = TransferConfig(
    multipart_threshold=8 * 1024 * 1024,  # fichiers >8MB en multipart
    max_concurrency=2,  # nombre de threads
    multipart_chunksize=8 * 1024 * 1024,  # taille des chunks
    use_threads=True,
)


class S3Connector(BaseFileConnector):
    def __init__(self, s3_client: boto3.client = None, bucket_name: str = "mybucket"):
        super().__init__()
        self.client = s3_client or boto3.client("s3")
        self.bucket_name = bucket_name
        self.up_time = datetime.datetime.now().isoformat()

        try:
            self.client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = int(e.response["Error"]["Code"])
            if error_code == 404:
                self.client.create_bucket(Bucket=self.bucket_name)
            else:
                raise e

    def get_by_task_id(self, user_id: str, task_id: str) -> str:
        object_key = f"{user_id}/{task_id}"
        try:
            metadata = self.client.head_object(Bucket=self.bucket_name, Key=object_key)
            logger.debug(f"{task_id} - {metadata['ContentLength']}")
            tmp_file = tempfile.NamedTemporaryFile(delete=False)
            tmp_file_path = tmp_file.name
            tmp_file.close()  # Important, boto3 va l’écrire
            logger.debug(f"{task_id} - Start to save chunk")
            self.client.download_file(self.bucket_name, object_key, tmp_file_path, Config=config)

            return tmp_file_path
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise FileNotFoundError(f"{object_key} non trouvé : {e}")
            raise FileNotFoundError(f"{object_key} non trouvé : {e}")

        except Exception as e:
            raise e

    def download_by_s3_key(self, s3_key: str) -> str:
        try:
            metadata = self.client.head_object(Bucket=self.bucket_name, Key=s3_key)
            logger.debug(f"{s3_key} - {metadata['ContentLength']}")
            tmp_file = tempfile.NamedTemporaryFile(delete=False)
            tmp_file_path = tmp_file.name
            tmp_file.close()  # Important, boto3 va l’écrire
            logger.debug(f"{s3_key} - Start to save chunk")
            self.client.download_file(self.bucket_name, s3_key, tmp_file_path, Config=config)

            return tmp_file_path
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise FileNotFoundError(f"{s3_key} non trouvé : {e}")
            raise FileNotFoundError(f"{s3_key} non trouvé : {e}")

        except Exception as e:
            raise e

    def get_object_bytes(self, s3_key: str) -> bytes:
        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=s3_key)
            return response["Body"].read()
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise FileNotFoundError(f"{s3_key} non trouvé : {e}")
            raise FileNotFoundError(f"{s3_key} non trouvé : {e}")

    def save(self, user_id: str, task_id: str, file_path: str, filename: str | None = None) -> str:
        if filename:
            filename = os.path.basename(filename)
        else:
            filename = os.path.basename(file_path)
        object_key = f"{user_id}/{task_id}/{filename}"
        try:
            self.client.upload_file(file_path, self.bucket_name, object_key)
            return object_key
        except ClientError as e:
            raise Exception(f"Erreur lors de la sauvegarde du fichier : {e}")

    def delete_by_task_id(self, user_id: str, task_id: str) -> bool:
        """Delete everything stored for a task: the uploaded file (`<user>/<task>/<filename>`)
        and the rendered page images (`<user>/<task>/images/...`)."""
        prefix = f"{user_id}/{task_id}/"
        # Also the bare `<user>/<task>` key that files were stored under before the filename
        # became part of the key.
        keys = [f"{user_id}/{task_id}"]
        paginator = self.client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
            keys.extend(obj["Key"] for obj in page.get("Contents", []))

        self._delete_keys(keys)
        return True

    def delete_by_s3_key(self, s3_key: str) -> bool:
        """Delete a single object by its key."""
        self._delete_keys([s3_key])
        return True

    def _delete_keys(self, keys: list[str]) -> None:
        batch_size = 1_000  # S3 DeleteObjects accepts at most 1000 keys per call.
        for start in range(0, len(keys), batch_size):
            response = self.client.delete_objects(
                Bucket=self.bucket_name,
                Delete={"Objects": [{"Key": key} for key in keys[start : start + batch_size]], "Quiet": True},
            )
            if response.get("Errors"):
                raise Exception(f"Erreur lors de la suppression de fichiers dans S3 : {response['Errors']}")

    def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        return self.client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": self.bucket_name, "Key": key},
            ExpiresIn=expires_in,
        )

    def get_health(self) -> Health:
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
        except Exception as error:
            return Health(
                name="s3",
                extras={"error": str(error)},
                version=boto3.__version__,
                up_time=self.up_time,
                status="unhealthy",
            )
        return Health(name="s3", version=boto3.__version__, up_time=self.up_time, status="healthy")

    def delete_by_user_id(self, user_id: str) -> bool:
        batch_delete_size: int = 1_000
        try:
            paginator = self.client.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=self.bucket_name, Prefix=f"{user_id}/")

            delete_us = dict(Objects=[])
            for page in pages:
                for obj in page.get("Contents", []):
                    delete_us["Objects"].append(dict(Key=obj["Key"]))
                    if len(delete_us["Objects"]) >= batch_delete_size:
                        self.client.delete_objects(Bucket=self.bucket_name, Delete=delete_us)
                        delete_us = dict(Objects=[])

            if delete_us["Objects"]:
                self.client.delete_objects(Bucket=self.bucket_name, Delete=delete_us)

            return True
        except ClientError as e:
            raise Exception(f"Erreur lors de la suppression des fichiers pour l'utilisateur {user_id} : {e}")


s3_settings = S3Settings()
