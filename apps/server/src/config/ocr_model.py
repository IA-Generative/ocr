from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class OCRModelSettings(BaseSettings):
    MODEL_NAME: Literal["paddle", "surya"] = "paddle"
    model_config = SettingsConfigDict(from_attributes=True, case_sensitive=True, env_file=".env", extra="allow")
