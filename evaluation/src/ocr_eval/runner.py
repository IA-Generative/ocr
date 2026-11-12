"""Run a task over each dataset and build one report per dataset."""

import logging
import time
from contextlib import ExitStack
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean

from ocr_eval import cache, hardware
from ocr_eval.config import DatasetConfig, RunConfig
from ocr_eval.dataset import load_samples
from ocr_eval.models import MODELS, Model
from ocr_eval.profiling import Profiler, image_stats, summarize
from ocr_eval.report import report_dir
from ocr_eval.tasks import TASKS, Task

log = logging.getLogger("ocr_eval")


def run(cfg: RunConfig, out_dir: str | Path = "reports", force: bool = False) -> list[dict]:
    """Evaluate the model on every dataset, one report each.

    A dataset whose fingerprint matches the report already in `out_dir` is not re-run (see
    `ocr_eval.cache`); `force=True` re-runs everything. The model is loaded lazily, only if at
    least one dataset has to be evaluated.
    """
    if cfg.task not in TASKS:
        raise ValueError(f"Unknown task {cfg.task!r}, available: {sorted(TASKS)}")
    if cfg.model.type not in MODELS:
        raise ValueError(f"Unknown model {cfg.model.type!r}, available: {sorted(MODELS)}")
    task = TASKS[cfg.task](cfg)
    model = MODELS[cfg.model.type](cfg.model.params)
    hw = hardware.collect(cfg.hardware)
    model_fp = model.fingerprint()

    reports = []
    with ExitStack() as stack:
        loaded = False
        for ds in cfg.datasets:
            revision = cache.dataset_revision(ds)
            fp = cache.fingerprint(cfg, ds, model_fp, hw, revision)
            path = report_dir(out_dir, cfg.name, ds.slug) / "report.json"
            hit = None if force else cache.load_cached(path, fp)
            if hit is not None:
                log.info("[%s] unchanged, reusing %s", ds.slug, path)
                # Thresholds may have changed even though the scores did not.
                hit["failures"] = task.check(hit["summary"], ds.thresholds or cfg.thresholds)
                hit["passed"] = not hit["failures"]
                hit["_cached"] = True
                reports.append(hit)
                continue
            if not loaded:
                stack.enter_context(model)
                loaded = True
            report = run_dataset(cfg, ds, task, model, hw)
            report.update(fingerprint=fp, dataset_revision=revision)
            reports.append(report)
    return reports


def run_dataset(cfg: RunConfig, ds: DatasetConfig, task: Task, model: Model, hw: dict) -> dict:
    samples, errors = [], []
    started = time.time()
    profiler = Profiler(cfg.profiling, f"{cfg.name}-{ds.slug}")
    with profiler:
        for sample in load_samples(ds):
            try:
                with profiler.measure(sample.id) as m:
                    prediction = model.predict(sample)
                scores = task.score(sample, prediction)
            except Exception as exc:  # noqa: BLE001 - one bad sample must not kill the run
                log.warning("[%s] sample %s failed: %s", ds.slug, sample.id, exc)
                errors.append({"id": sample.id, "error": str(exc)})
                continue
            profile = {**image_stats(*sample.image.size), **asdict(m)}
            samples.append(
                {
                    "id": sample.id,
                    "reference": sample.reference,
                    "prediction": prediction.text,
                    **scores,
                    "profile": profile,
                }
            )
            log.info("[%s] sample %s: %s", ds.slug, sample.id, scores)

    summary = {k: mean(s[k] for s in samples) for k in _metric_keys(samples)}
    thresholds = ds.thresholds or cfg.thresholds
    failures = task.check(summary, thresholds) if samples else ["no sample was evaluated"]
    return {
        "name": cfg.name,
        "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "task": cfg.task,
        "model": cfg.model.model_dump(exclude={"api_key"}),
        "dataset": ds.model_dump(),
        "duration_s": round(time.time() - started, 2),
        "n_evaluated": len(samples),
        "n_errors": len(errors),
        "hardware": hw,
        "summary": summary,
        "profiling": {**summarize(samples), **profiler.run_totals()},
        "failures": failures,
        "passed": not failures,
        "samples": samples,
        "errors": errors,
    }


def _metric_keys(samples: list[dict]) -> list[str]:
    return [
        k
        for k in (samples[0] if samples else {})
        if k not in ("id", "reference", "prediction", "profile")
    ]
