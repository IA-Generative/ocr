"""Model backends: anything that turns a Sample image into a normalized `Prediction`.

A task never knows where the model runs. A backend can be the deployed API or a model
loaded in-process (no API involved).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, ClassVar

from ocr_eval.dataset.base import Sample, Word


@dataclass
class Prediction:
    text: str
    # Words with bboxes in image pixels [xmin, ymin, xmax, ymax]; empty if the model has none.
    words: list[Word] = field(default_factory=list)


class Model(ABC):
    """Lifecycle: `load()` once (weights, client), `predict()` per sample, `close()` at the end."""

    name: ClassVar[str]

    def __init__(self, params: dict[str, Any]):
        self.params = params

    def load(self) -> None:
        """Load weights / open connections. Kept out of __init__ so config errors fail fast."""

    @abstractmethod
    def predict(self, sample: Sample) -> Prediction: ...

    def close(self) -> None:
        pass

    def fingerprint(self) -> dict | None:
        """Everything that determines this model's outputs (config, library versions, weights).

        Called before `load()`. Two runs with the same fingerprint are assumed to give the same
        scores, which is what lets the runner skip an unchanged evaluation. Return None when
        that cannot be guaranteed (e.g. a remote API whose server may change): the model is
        then always re-evaluated.
        """
        return None

    def __enter__(self):
        self.load()
        return self

    def __exit__(self, *exc):
        self.close()


class LocalModel(Model):
    """Base for models run in-process. Subclass, implement `load()` and `predict()`.

    Heavy imports (torch, transformers, paddle...) belong inside `load()` so that the
    registry can be imported without them. `device` comes from the config.
    """

    def fingerprint(self) -> dict | None:
        return {"type": self.name, "params": self.params}

    @property
    def device(self) -> str:
        return self.params.get("device", "cpu")
