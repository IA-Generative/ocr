"""Decide which configs the CI has to run, so a PR only evaluates what it touches."""

import json
from pathlib import Path

from ocr_eval.config import load_config

# `uv sync --extra` each model type needs, so a job installs only its own runtime
# (Tesseract also needs apt packages).
MODEL_EXTRAS = {"paddleocr_onnx": "paddle", "tesseract": "tesseract"}

# A change here can alter any model's scores (or how every report is rendered), so every
# CI config is re-evaluated. Paths are relative to the repository root.
GLOBAL_TRIGGERS = (
    "evaluation/src/",
    "evaluation/pyproject.toml",
    "evaluation/uv.lock",
    ".github/workflows/evaluation.yml",
)


def plan(
    eval_dir: str | Path,
    changed_files: list[str],
    run_all: bool = False,
    reports_dir: str | Path | None = None,
) -> list[dict]:
    """Configs to run, as [{"config": "configs/x.yaml", "name": "x", "extra": "paddle"}].

    Only configs with `ci: true` are candidates. A config is selected when:
      - `run_all` is set (scheduled / manual / main runs: unchanged ones then skip cheaply
        thanks to the fingerprint cache), or
      - the evaluation code or its dependencies changed, or
      - the config file itself was added or modified, or
      - it has never produced a report (the first run launches everything).
    """
    eval_dir = Path(eval_dir)
    reports_dir = Path(reports_dir) if reports_dir else eval_dir / "reports"
    global_change = any(f.startswith(GLOBAL_TRIGGERS) for f in changed_files)

    selected = []
    for path in sorted((eval_dir / "configs").glob("*.yaml")):
        cfg = load_config(path)
        if not cfg.ci:
            continue
        rel = f"evaluation/configs/{path.name}"
        never_run = not (reports_dir / cfg.name / "index.json").exists()
        if run_all or global_change or rel in changed_files or never_run:
            selected.append(
                {
                    "config": f"configs/{path.name}",
                    "name": cfg.name,
                    "extra": MODEL_EXTRAS.get(cfg.model.type, ""),
                }
            )
    return selected


def to_matrix(selected: list[dict]) -> str:
    return json.dumps({"include": selected}, separators=(",", ":"))
