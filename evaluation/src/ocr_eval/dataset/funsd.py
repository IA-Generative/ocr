from typing import ClassVar

from ocr_eval.dataset.generic import GenericAdapter


class FunsdAdapter(GenericAdapter):
    """nielsr/funsd-layoutlmv3: `tokens` + `bboxes` normalized to 0..1000."""

    name: ClassVar[str] = "funsd"
    default_text_column = "tokens"
    default_bboxes_column = "bboxes"
    default_bbox_scale = "norm1000"
