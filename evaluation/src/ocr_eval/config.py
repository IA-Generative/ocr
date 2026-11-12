"""Run configuration, loaded from YAML and validated with pydantic."""

import re
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field

from ocr_eval.hardware import HardwareConfig
from ocr_eval.profiling import ProfilingConfig


class ModelConfig(BaseModel):
    """Which backend runs the model. `type` selects it in `ocr_eval.models.MODELS`; every
    other key is passed to the backend as its parameters (api: base_url, timeout...;
    a local model: device, weights path...)."""

    model_config = ConfigDict(extra="allow")
    type: str = "api"

    @property
    def params(self) -> dict:
        return dict(self.model_extra or {})


class Thresholds(BaseModel):
    cer_max: float | None = None
    wer_max: float | None = None


class DatasetConfig(BaseModel):
    name: str
    config: str | None = None
    split: str = "test"
    label: str | None = None  # report file name; defaults to "<name>__<split>"
    thresholds: Thresholds | None = None  # overrides the run-level thresholds for this dataset
    max_samples: int | None = Field(default=None, ge=1)
    seed: int = 42
    # Very large datasets (hundreds of GB) must be streamed instead of downloaded. The shuffle
    # is then approximate (a buffer of `shuffle_buffer` rows) but deterministic for a given seed.
    streaming: bool = False
    shuffle_buffer: int = Field(default=100, ge=1)
    # Document datasets only: pages sampled per document (`max_samples` counts pages).
    pages_per_document: int = Field(default=1, ge=1)

    # Schema normalization. `adapter` selects the class in `ocr_eval.dataset` that maps a raw
    # row to a Sample; the fields below are only needed to override its defaults
    # (`generic` has no schema knowledge, so it relies on them).
    adapter: str = "generic"
    image_column: str = "image"
    text_column: str = "text"  # a string, or a list of words
    bboxes_column: str | None = None  # one bbox per word, aligned with text_column
    bbox_format: str = "xyxy"  # xyxy | xywh
    bbox_scale: str = "pixel"  # pixel | norm1 | norm1000

    @property
    def slug(self) -> str:
        raw = self.label or f"{self.name}__{self.split}"
        return re.sub(r"[^A-Za-z0-9._-]+", "_", raw)


class RunConfig(BaseModel):
    name: str
    # Opt-in for the CI workflow (which runs it on a runner). Configs needing an API or a
    # GPU stay `false` and are only run by hand.
    ci: bool = False
    task: str = "ocr"
    model: ModelConfig = Field(default_factory=ModelConfig)
    datasets: list[DatasetConfig] = Field(min_length=1)  # one report per dataset
    thresholds: Thresholds = Field(default_factory=Thresholds)
    profiling: ProfilingConfig = Field(default_factory=ProfilingConfig)
    hardware: HardwareConfig = Field(default_factory=HardwareConfig)


def load_config(path: str | Path) -> RunConfig:
    with open(path, encoding="utf-8") as f:
        return RunConfig.model_validate(yaml.safe_load(f))
