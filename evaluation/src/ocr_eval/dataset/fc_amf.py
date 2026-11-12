"""lightonai/fc-amf-ocr: French/English financial filings, PDF + docTR OCR output.

A row is a whole document: `pdf` (bytes) and `json.gz` (pages -> blocks -> lines -> words, each
word with a confidence and a normalized [[x0, y0], [x1, y1]] box). We render the PDF pages at
144 DPI, the resolution docTR ran at, so the boxes map exactly onto the image.

!! The reference is another OCR's output, not a human transcription: scores measure agreement
with docTR, and its errors are counted as the evaluated model's errors. Words follow docTR's
stored order (blocks, then lines, then words), which is not guaranteed to be reading order.

Needs `streaming: true` (the dataset is ~440 GB). `max_samples` counts pages.
"""

import random
from collections.abc import Iterator
from typing import Any, ClassVar

import pymupdf
from PIL import Image

from ocr_eval.dataset.base import DatasetAdapter, Sample, Word

DPI = 144  # resolution the reference OCR was run at


class FcAmfAdapter(DatasetAdapter):
    name: ClassVar[str] = "fc_amf"

    def iter_samples(self, row: dict[str, Any], index: int) -> Iterator[Sample]:
        key = row.get("__key__", str(index))
        pages = {p["page_idx"]: p for p in row["json.gz"]["pages"]}
        # Seeded per document, so the same pages are picked on every run.
        rng = random.Random(f"{self.cfg.seed}:{key}")
        order = sorted(pages)
        rng.shuffle(order)

        doc = pymupdf.open(stream=row["pdf"], filetype="pdf")
        yielded = 0
        for idx in order:
            words = _words(pages[idx])
            if not words or idx >= len(doc):  # blank / unreadable page: nothing to compare
                continue
            pix = doc[idx].get_pixmap(dpi=DPI, colorspace=pymupdf.csRGB)
            image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            w, h = image.size
            yield Sample(
                id=f"{key}#p{idx}",
                image=image,
                words=[Word(t, [x0 * w, y0 * h, x1 * w, y1 * h]) for t, (x0, y0, x1, y1) in words],
            )
            yielded += 1
            if yielded >= self.cfg.pages_per_document:
                return


def _words(page: dict) -> list[tuple[str, tuple[float, float, float, float]]]:
    out = []
    for block in page["blocks"]:
        for line in block["lines"]:
            for w in line["words"]:
                (x0, y0), (x1, y1) = w["geometry"]
                out.append((w["value"], (x0, y0, x1, y1)))
    return out
