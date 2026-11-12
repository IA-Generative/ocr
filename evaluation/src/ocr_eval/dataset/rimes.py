from typing import ClassVar

from ocr_eval.dataset.generic import GenericAdapter


class RimesAdapter(GenericAdapter):
    """Teklia/RIMES-2011-line: handwritten French text lines, `image` + `text` (a string).

    Line-level, no boxes: only text metrics (CER / WER) apply.
    """

    name: ClassVar[str] = "rimes"
    default_image_column = "image"
    default_text_column = "text"
