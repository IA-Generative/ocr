from abc import ABC, abstractmethod

from ocr_eval.config import RunConfig, Thresholds
from ocr_eval.dataset import Sample
from ocr_eval.models import Prediction


class Task(ABC):
    """What is measured: scores a Prediction against a Sample's reference.

    Running the model is the backend's job (`ocr_eval.models`), so the same task works
    for the API and for any local model.
    """

    def __init__(self, cfg: RunConfig):
        self.cfg = cfg

    @abstractmethod
    def score(self, sample: Sample, prediction: Prediction) -> dict[str, float]:
        """Per-sample metrics."""

    @abstractmethod
    def check(self, summary: dict[str, float], thresholds: Thresholds) -> list[str]:
        """Return a list of threshold violations (empty = pass)."""
