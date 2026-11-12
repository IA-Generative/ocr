"""The deployed OCR API, through ocr-sdk."""

import os
import tempfile
from pathlib import Path
from typing import ClassVar

from ocr_sdk import SyncOCRClient, TaskOperation
from pydantic import BaseModel

from ocr_eval.dataset.base import Sample, Word
from ocr_eval.models.base import Model, Prediction


class ApiParams(BaseModel):
    base_url: str = "http://localhost:5000"
    api_key: str | None = None
    timeout: float = 60.0
    max_wait_time: float = 300.0
    poll_interval: float = 2.0
    operation: str = "ocr"


class ApiModel(Model):
    name: ClassVar[str] = "api"

    def __init__(self, params):
        super().__init__(params)
        p = ApiParams.model_validate(params)
        # Environment wins over the file so CI can target any deployment without editing configs.
        p.base_url = os.environ.get("OCR_API_URL", p.base_url)
        p.api_key = os.environ.get("OCR_API_KEY", p.api_key)
        self.p = p

    def load(self) -> None:
        self._client = SyncOCRClient(
            self.p.base_url, api_key=self.p.api_key, timeout=self.p.timeout
        ).__enter__()

    def predict(self, sample: Sample) -> Prediction:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / f"{sample.id}.png"
            sample.image.save(path)
            job = self._client.create_job(path, task_operation=TaskOperation(self.p.operation))
        task = self._client.wait_for_task(
            job.id, poll_interval=self.p.poll_interval, max_wait_time=self.p.max_wait_time
        )
        words = []
        if task.output is not None:
            for page in task.output.pages:
                # API boxes are x, y, width, height
                words += [
                    Word(b.text, [b.x, b.y, b.x + b.width, b.y + b.height]) for b in page.boxes
                ]
        return Prediction(text=self._client.get_task_text(job.id), words=words)

    def close(self) -> None:
        self._client.__exit__(None, None, None)
