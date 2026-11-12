"""Text metrics."""

import re

import jiwer


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def cer(reference: str, hypothesis: str) -> float:
    reference, hypothesis = normalize(reference), normalize(hypothesis)
    if not reference:
        return 0.0 if not hypothesis else 1.0
    return float(jiwer.cer(reference, hypothesis))


def wer(reference: str, hypothesis: str) -> float:
    reference, hypothesis = normalize(reference), normalize(hypothesis)
    if not reference:
        return 0.0 if not hypothesis else 1.0
    return float(jiwer.wer(reference, hypothesis))
