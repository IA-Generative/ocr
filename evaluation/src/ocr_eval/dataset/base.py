"""Normalized sample schema and the adapter contract.

Every HuggingFace dataset has its own schema. An adapter turns one raw row into a `Sample`,
so tasks and metrics only ever see this one shape.
"""

from abc import ABC
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any, ClassVar

from PIL import Image

from ocr_eval.config import DatasetConfig


@dataclass
class Word:
    text: str
    # [xmin, ymin, xmax, ymax] in image pixels (None if the dataset has no boxes).
    bbox: list[float] | None = None


@dataclass
class Sample:
    id: str
    image: Image.Image
    words: list[Word] = field(default_factory=list)

    @property
    def reference(self) -> str:
        return " ".join(w.text for w in self.words)

    @property
    def bboxes(self) -> list[list[float]]:
        return [w.bbox for w in self.words if w.bbox is not None]


def normalize_bbox(bbox: list[float], fmt: str, scale: str, width: int, height: int) -> list[float]:
    """Convert a raw bbox to [xmin, ymin, xmax, ymax] in pixels.

    fmt:   "xyxy" (xmin, ymin, xmax, ymax) or "xywh" (xmin, ymin, width, height)
    scale: "pixel", "norm1" (0..1) or "norm1000" (0..1000, LayoutLM style)
    """
    a, b, c, d = (float(v) for v in bbox)
    if fmt == "xywh":
        c, d = a + c, b + d
    elif fmt != "xyxy":
        raise ValueError(f"unknown bbox_format {fmt!r}")
    factor = {"pixel": (1, 1), "norm1": (width, height), "norm1000": (width / 1000, height / 1000)}
    if scale not in factor:
        raise ValueError(f"unknown bbox_scale {scale!r}")
    fx, fy = factor[scale]
    return [a * fx, b * fy, c * fx, d * fy]


class DatasetAdapter(ABC):
    """Maps one raw HF row to a `Sample`. Subclasses declare their schema defaults."""

    name: ClassVar[str]

    def __init__(self, cfg: DatasetConfig):
        self.cfg = cfg

    def to_sample(self, row: dict[str, Any], index: int) -> Sample:
        """One row = one sample (most datasets). Implement this or `iter_samples`."""
        raise NotImplementedError

    def iter_samples(self, row: dict[str, Any], index: int) -> Iterator[Sample]:
        """One row -> any number of samples (e.g. a multi-page document -> one per page)."""
        yield self.to_sample(row, index)
