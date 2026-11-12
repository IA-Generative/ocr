from ocr_eval.models.api import ApiModel
from ocr_eval.models.base import LocalModel, Model, Prediction
from ocr_eval.models.paddleocr_onnx import PaddleOcrOnnxModel
from ocr_eval.models.tesseract import TesseractModel

# Register new backends (local models included) here. Import heavy deps inside `load()`.
MODELS: dict[str, type[Model]] = {a.name: a for a in (ApiModel, PaddleOcrOnnxModel, TesseractModel)}

__all__ = ["MODELS", "ApiModel", "LocalModel", "Model", "Prediction"]
