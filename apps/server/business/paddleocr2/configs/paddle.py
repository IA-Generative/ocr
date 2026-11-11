from pydantic_settings import BaseSettings, SettingsConfigDict


class PaddleSetting(BaseSettings):
    PADDLE_OCR_BASE_DIR: str = "models/"
    PADDLE_PDX_CACHE_HOME: str = "models/paddle_pdx_cache/"
    DETECTION_FOLDER: str = "detection"
    RECOGNITION_FOLDER: str = "recognition"
    CLASSIFICATION_FOLDER: str = "classification"
    DETECTION_BATCH_SIZE: int = 2
    RECOGNITION_BATCH_SIZE: int = 8
    CPU_THREADS: int = 2
    ENABLE_MKLDNN: bool = False
    # PP-OCRv6 tiny, exécuté via ONNX Runtime (variantes `_onnx` téléchargées automatiquement
    # par PaddleX quand `OCR_ENGINE="onnxruntime"`). Passer `OCR_ENGINE=paddle` pour revenir
    # au moteur Paddle Inference avec les modèles natifs.
    OCR_ENGINE: str = "onnxruntime"
    TEXT_DETECTION_MODEL_NAME: str = "PP-OCRv6_tiny_det"
    TEXT_RECOGNITION_MODEL_NAME: str = "PP-OCRv6_tiny_rec"
    LAYOUT_MODEL_NAME: str = "PP-DocLayoutV2"
    DEVICE: str = "cpu"
    CLIP_MODEL_DIR: str = "/app/models/clip"
    OCR_LANG: str | None = None
    model_config = SettingsConfigDict(from_attributes=True, case_sensitive=True, env_file=".env", extra="allow")


def build_paddle_ocr_kwargs(settings: PaddleSetting) -> dict:
    """Arguments de `PaddleOCR(...)` communs au service et au script de téléchargement.

    Les noms de modèles sont explicites (PP-OCRv6 tiny) : `lang`/`ocr_version` sont alors
    ignorés par PaddleOCR (le modèle v6 tiny est multilingue, dont le français).
    """
    kwargs: dict = {
        "text_detection_model_name": settings.TEXT_DETECTION_MODEL_NAME,
        "text_recognition_model_name": settings.TEXT_RECOGNITION_MODEL_NAME,
        "engine": settings.OCR_ENGINE,
        "device": settings.DEVICE,
    }
    if settings.OCR_ENGINE == "onnxruntime":
        # cpu_threads / enable_mkldnn ne concernent que Paddle Inference.
        kwargs["engine_config"] = {"intra_op_num_threads": settings.CPU_THREADS}
    else:
        kwargs["cpu_threads"] = settings.CPU_THREADS
        kwargs["enable_mkldnn"] = settings.ENABLE_MKLDNN
    return kwargs
