"""Tesseract, run in-process through pytesseract (no API).

Needs the `tesseract` extra (`uv sync --extra tesseract`) and the tesseract binary with the
language data installed (apt: `tesseract-ocr tesseract-ocr-fra`). Params (all optional):

    type: tesseract
    lang: fra            # "fra", or several combined: "fra+eng"
    psm: 3               # page segmentation: 3 = auto page, 7 = a single text line
    oem: 1               # engine: 1 = LSTM only
    min_conf: 0          # drop words below this confidence (0-100)
    threads: 1           # OMP_THREAD_LIMIT; 1 is Tesseract's recommendation and keeps runs
                         # reproducible and timings comparable
"""

import hashlib
import os
import subprocess
from pathlib import Path
from typing import ClassVar

from ocr_eval.dataset.base import Sample, Word
from ocr_eval.models.base import LocalModel, Prediction

DEFAULTS = {"lang": "fra", "psm": 3, "oem": 1, "min_conf": 0, "threads": 1}


def _tessdata_dir() -> Path | None:
    out = subprocess.run(
        ["tesseract", "--list-langs"], capture_output=True, text=True, check=False
    ).stdout
    # First line: 'List of available languages in "/path/tessdata/" (3):'
    if '"' in out:
        return Path(out.split('"')[1])
    return None


class TesseractModel(LocalModel):
    name: ClassVar[str] = "tesseract"

    @property
    def p(self) -> dict:
        return {**DEFAULTS, **self.params}

    def fingerprint(self) -> dict:
        version = None
        weights = {}
        try:
            out = subprocess.run(
                ["tesseract", "--version"], capture_output=True, text=True, check=False
            )
            version = (out.stdout or out.stderr).splitlines()[0]
            tessdata = _tessdata_dir()
            for lang in str(self.p["lang"]).split("+"):
                f = tessdata / f"{lang}.traineddata" if tessdata else None
                weights[lang] = (
                    hashlib.sha256(f.read_bytes()).hexdigest() if f and f.exists() else None
                )
        except OSError:  # binary missing: load() raises a clear error
            pass
        return {"type": self.name, "params": self.p, "version": version, "weights": weights}

    def load(self) -> None:
        import pytesseract  # optional extra

        self._tess = pytesseract
        os.environ["OMP_THREAD_LIMIT"] = str(self.p["threads"])
        try:
            available = set(pytesseract.get_languages())
        except pytesseract.TesseractNotFoundError as exc:
            raise RuntimeError("tesseract binary not found (apt install tesseract-ocr)") from exc
        missing = set(str(self.p["lang"]).split("+")) - available
        if missing:
            raise RuntimeError(
                f"tesseract language data missing: {sorted(missing)} "
                f"(apt install tesseract-ocr-{min(missing)}); available: {sorted(available)}"
            )

    def predict(self, sample: Sample) -> Prediction:
        p = self.p
        data = self._tess.image_to_data(
            sample.image,
            lang=p["lang"],
            config=f"--psm {p['psm']} --oem {p['oem']}",
            output_type=self._tess.Output.DICT,
        )
        words = []
        for i, text in enumerate(data["text"]):
            conf = float(data["conf"][i])
            # conf == -1 marks layout rows (block / line), not words
            if not text.strip() or conf < 0 or conf < p["min_conf"]:
                continue
            x, y, w, h = (data[k][i] for k in ("left", "top", "width", "height"))
            words.append(Word(text.strip(), [float(x), float(y), float(x + w), float(y + h)]))
        return Prediction(text=" ".join(w.text for w in words), words=words)
