"""OCR text-extraction task: CER / WER against the dataset transcription."""

from ocr_eval import metrics
from ocr_eval.config import Thresholds
from ocr_eval.dataset import Sample
from ocr_eval.models import Prediction
from ocr_eval.tasks.base import Task


class OcrTask(Task):
    def score(self, sample: Sample, prediction: Prediction) -> dict[str, float]:
        return {
            "cer": metrics.cer(sample.reference, prediction.text),
            "wer": metrics.wer(sample.reference, prediction.text),
        }

    def check(self, summary: dict[str, float], thresholds: Thresholds) -> list[str]:
        failures = []
        if thresholds.cer_max is not None and summary["cer"] > thresholds.cer_max:
            failures.append(f"cer {summary['cer']:.4f} > {thresholds.cer_max}")
        if thresholds.wer_max is not None and summary["wer"] > thresholds.wer_max:
            failures.append(f"wer {summary['wer']:.4f} > {thresholds.wer_max}")
        return failures
