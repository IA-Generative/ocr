from pydantic_settings import BaseSettings, SettingsConfigDict


class LayoutSettings(BaseSettings):
    LAYOUT_MODEL_NAME: str = "PP-DocLayout_plus-L"
    LAYOUT_BATCH_SIZE: int = 2
    LAYOUT_SCORE_THRESHOLD: float = 0.5
    LAYOUT_PDF_DPI: int = 150
    LAYOUT_ENABLE_TABLES: bool = True
    # Le layout n'écrit en base qu'une fois l'OCR terminé : durée max d'attente de cette fin.
    LAYOUT_WAIT_OCR_TIMEOUT_S: int = 3600
    LAYOUT_WAIT_POLL_INTERVAL_S: float = 2.0
    DEVICE: str = "cpu"
    CPU_THREADS: int = 2
    ENABLE_MKLDNN: bool = False
    model_config = SettingsConfigDict(from_attributes=True, case_sensitive=True, env_file=".env", extra="allow")
