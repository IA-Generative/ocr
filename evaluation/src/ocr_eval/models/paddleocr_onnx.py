"""PaddleOCR (PP-OCRv6) run in-process on onnxruntime, no API and no paddlepaddle runtime.

Needs the `paddle` extra: `uv sync --extra paddle`. Weights are downloaded by PaddleOCR on
first use into ~/.paddlex. Params (all optional):

    type: paddleocr_onnx
    det_model: PP-OCRv6_tiny_det
    rec_model: PP-OCRv6_tiny_rec     # tiny | small | medium
    device: cpu                      # cpu | gpu (gpu needs onnxruntime-gpu)
"""

import hashlib
from importlib import metadata
from pathlib import Path
from typing import ClassVar

import numpy as np

from ocr_eval.dataset.base import Sample, Word
from ocr_eval.models.base import LocalModel, Prediction

DEFAULTS = {"det_model": "PP-OCRv6_tiny_det", "rec_model": "PP-OCRv6_tiny_rec", "device": "cpu"}


class PaddleOcrOnnxModel(LocalModel):
    name: ClassVar[str] = "paddleocr_onnx"

    def fingerprint(self) -> dict:
        def version(pkg: str) -> str | None:
            try:
                return metadata.version(pkg)
            except metadata.PackageNotFoundError:
                return None

        # Weights are hashed when already downloaded; before the first run only names count.
        weights = {}
        for key in ("det_model", "rec_model"):
            name = self.params.get(key, DEFAULTS[key])
            folder = Path.home() / ".paddlex" / "official_models" / f"{name}_onnx"
            files = sorted(folder.glob("*.onnx")) if folder.exists() else []
            weights[name] = [hashlib.sha256(f.read_bytes()).hexdigest() for f in files]
        return {
            "type": self.name,
            "params": {**DEFAULTS, **self.params},
            "libs": {p: version(p) for p in ("paddleocr", "paddlex", "onnxruntime")},
            "weights": weights,
        }

    def load(self) -> None:
        from paddleocr import PaddleOCR  # heavy, optional extra

        self._ocr = PaddleOCR(
            text_detection_model_name=self.params.get("det_model", DEFAULTS["det_model"]),
            text_recognition_model_name=self.params.get("rec_model", DEFAULTS["rec_model"]),
            engine="onnxruntime",
            device=self.device,
            # Documents are evaluated as given: no orientation / unwarping preprocessing.
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
        )

    def predict(self, sample: Sample) -> Prediction:
        bgr = np.asarray(sample.image)[:, :, ::-1]  # PaddleOCR expects BGR
        result = self._ocr.predict(bgr)[0]
        texts = result["rec_texts"]
        boxes = result["rec_boxes"]  # xyxy pixels, one per text line
        words = [Word(t, [float(v) for v in boxes[i]]) for i, t in enumerate(texts)]
        return Prediction(text=" ".join(texts), words=words)
