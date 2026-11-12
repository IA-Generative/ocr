"""Skip evaluations whose inputs did not change.

A report is reused when its fingerprint matches: same eval code, task, model (config, library
versions, weights), dataset config *and revision*, and same kind of machine. Scores are
deterministic given those (fixed shuffle seed, fixed sample selection), so rerunning would
only reproduce them. Thresholds are not part of the fingerprint: pass/fail is recomputed
from the cached scores.
"""

import functools
import hashlib
import json
from pathlib import Path

from ocr_eval.config import DatasetConfig, RunConfig

_PKG = Path(__file__).parent
# Report rendering and CLI do not influence scores.
_IGNORED = {"report.py", "cli.py", "cache.py", "plan.py", "compare.py", "charts.py"}


@functools.cache
def code_hash() -> str:
    h = hashlib.sha256()
    for f in sorted(_PKG.rglob("*.py")):
        if f.name not in _IGNORED:
            h.update(f.relative_to(_PKG).as_posix().encode())
            h.update(f.read_bytes())
    return h.hexdigest()


def dataset_revision(ds: DatasetConfig) -> str | None:
    """Commit sha of the HF dataset, so a silent upstream change invalidates the cache."""
    try:
        from huggingface_hub import HfApi

        return HfApi().dataset_info(ds.name).sha
    except Exception:  # noqa: BLE001 - offline / private: fall back to no revision
        return None


def fingerprint(
    cfg: RunConfig, ds: DatasetConfig, model_fp: dict | None, hw: dict, revision: str | None
) -> str | None:
    if model_fp is None:
        return None
    payload = {
        "code": code_hash(),
        "task": cfg.task,
        "model": model_fp,
        "dataset": ds.model_dump(exclude={"thresholds", "label"}),
        "revision": revision,
        # Timing and energy depend on the machine, so a report is not reused across hardware.
        # A declared label wins over the detected CPU: CI runners of one class (e.g.
        # "ubuntu-latest") have different CPU models from one run to the next, which would
        # otherwise invalidate the cache every time.
        "machine": hw["label"] or {k: hw[k] for k in ("cpu_model", "accelerator", "gpus")},
    }
    blob = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()


def load_cached(report_json: Path, fp: str | None) -> dict | None:
    if fp is None or not report_json.exists():
        return None
    try:
        report = json.loads(report_json.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return report if report.get("fingerprint") == fp else None
