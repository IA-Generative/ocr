"""Write reports: report.json + a human-readable README.md per dataset, and a run index."""

import json
from pathlib import Path

from ocr_eval.config import DatasetConfig

WORST_N = 5


def report_dir(out_dir: str | Path, run_name: str, slug: str) -> Path:
    return Path(out_dir) / run_name / slug


def _cell(text: object, limit: int = 90) -> str:
    s = str(text).replace("\n", " ").replace("|", "\\|")
    return s if len(s) <= limit else s[: limit - 1] + "…"


def _fmt(value: float | None, spec: str = ".4f") -> str:
    return "n/a" if value is None else format(value, spec)


def render_dataset_md(r: dict) -> str:
    ds, hw, prof = r["dataset"], r["hardware"], r["profiling"]
    gpus = ", ".join(f"{g['name']} ({g['memory_gb']} GB)" for g in hw["gpus"]) or "none"
    status = "✅ passed" if r["passed"] else "❌ failed"
    lines = [
        f"# {r['name']} — {ds['name']} ({ds['split']})",
        "",
        f"**Date:** {r['created_at']}  ",
        f"**Status:** {status}  ",
        (
            f"**Samples:** {r['n_evaluated']} evaluated, {r['n_errors']} errors "
            f"(seed {ds['seed']}, max_samples {ds['max_samples']})  "
        ),
        (
            f"**Dataset:** [{ds['name']}](https://huggingface.co/datasets/{ds['name']}) "
            f"· revision `{(r['dataset_revision'] or 'unknown')[:12]}`  "
        ),
        f"**Model:** `{r['model']['type']}` "
        + ", ".join(f"{k}={v}" for k, v in r["model"].items() if k != "type"),
        "",
    ]
    if r["failures"]:
        lines += ["**Failures:**", *[f"- {f}" for f in r["failures"]], ""]

    lines += ["## Scores", "", "| Metric | Value |", "|---|---|"]
    lines += [f"| {k} | {v:.4f} |" for k, v in r["summary"].items()]

    if prof:
        lines += [
            "",
            "## Speed and energy",
            "",
            "| | |",
            "|---|---|",
            f"| Inference mean | {prof['inference_s_mean']:.3f}s |",
            (
                f"| Inference p50 / p90 / p95 / p99 | {prof['inference_s_p50']:.3f}s / "
                f"{prof['inference_s_p90']:.3f}s / {prof['inference_s_p95']:.3f}s / "
                f"{prof['inference_s_p99']:.3f}s |"
            ),
            f"| Inference max | {prof['inference_s_max']:.3f}s |",
            f"| Seconds per megapixel | {prof['s_per_megapixel']:.3f} |",
            f"| Energy | {_fmt(prof.get('energy_kwh_total'), '.6f')} kWh |",
            f"| Emissions | {_fmt(prof.get('emissions_kg_total'), '.6f')} kgCO2eq |",
            "",
            "| Image size | Samples | Mean inference | p95 |",
            "|---|---|---|---|",
        ]
        lines += [
            f"| {k} | {b['n']} | {b['inference_s_mean']:.3f}s | {b['inference_s_p95']:.3f}s |"
            for k, b in prof["by_image_size"].items()
        ]

    lines += [
        "",
        "## Hardware",
        "",
        "| | |",
        "|---|---|",
        f"| Label | {hw['label'] or '—'} |",
        (
            f"| CPU | {hw['cpu_model']} ({hw['cpu_cores_physical']} cores, "
            f"{hw['cpu_cores_logical']} threads) |"
        ),
        f"| RAM | {hw['ram_gb']} GB |",
        f"| GPU | {gpus} |",
        f"| OS / Python | {hw['os']} / {hw['python']} |",
        f"| Libraries | {', '.join(f'{k} {v}' for k, v in hw['libs'].items() if v) or '—'} |",
        "",
        "Energy figures are estimates when CPU power counters are not readable (RAPL).",
    ]

    key = next(iter(r["summary"]), None)
    worst = r.get("worst_samples", [])
    if key and worst:
        lines += [
            "",
            f"## Worst samples (by {key})",
            "",
            f"| Id | {key} | Reference | Prediction |",
            "|---|---|---|---|",
        ]
        lines += [
            f"| {_cell(s['id'], 20)} | {s[key]:.3f} | {_cell(s['reference'])} "
            f"| {_cell(s['prediction'])} |"
            for s in worst
        ]
    if r["errors"]:
        lines += ["", "## Errors", ""] + [
            f"- `{e['id']}`: {_cell(e['error'], 200)}" for e in r["errors"]
        ]
    lines += [
        "",
        f"Full data: [report.json](report.json) (per-sample details: `samples.jsonl`, not versioned) · fingerprint `{(r['fingerprint'] or 'none')[:12]}`",
        "",
    ]
    return "\n".join(lines)


def render_index_md(reports: list[dict], slugs: list[str]) -> str:
    first = reports[0]
    lines = [
        f"# {first['name']}",
        "",
        f"Model: `{first['model']['type']}` · task: `{first['task']}`",
        "",
        "| Dataset | Date | Samples | Scores | Status |",
        "|---|---|---|---|---|",
    ]
    for r, slug in zip(reports, slugs):
        scores = ", ".join(f"{k} {v:.3f}" for k, v in r["summary"].items())
        lines.append(
            f"| [{r['dataset']['name']} ({r['dataset']['split']})]({slug}/README.md) "
            f"| {r['created_at']} | {r['n_evaluated']} | {scores} "
            f"| {'✅' if r['passed'] else '❌'} |"
        )
    return "\n".join(lines) + "\n"


def write_reports(reports: list[dict], out_dir: str | Path) -> list[Path]:
    """<out_dir>/<run>/<dataset>/{report.json,README.md}, plus <run>/{index.json,README.md}.

    Paths are stable across runs (the date lives inside the files), so an unchanged run
    rewrites identical content and git history only shows real changes.
    """
    run_dir = Path(out_dir) / reports[0]["name"]
    paths, index, slugs = [], [], []
    for r in reports:
        r.pop("_cached", None)
        slug = DatasetConfig.model_validate(r["dataset"]).slug
        d = report_dir(out_dir, r["name"], slug)
        d.mkdir(parents=True, exist_ok=True)
        # Per-sample data is bulky and noisy (timings change every run), so it stays out of the
        # versioned report.json; the worst samples are kept there for the README.
        samples = r.pop("samples", None)
        if samples is not None:
            key = next(iter(r["summary"]), None)
            r["worst_samples"] = (
                sorted(samples, key=lambda s: s[key], reverse=True)[:WORST_N] if key else []
            )
            (d / "samples.jsonl").write_text(
                "\n".join(json.dumps(s, ensure_ascii=False) for s in samples) + "\n",
                encoding="utf-8",
            )
        (d / "report.json").write_text(
            json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        (d / "README.md").write_text(render_dataset_md(r), encoding="utf-8")
        paths.append(d)
        slugs.append(slug)
        index.append(
            {
                "dataset": slug,
                "created_at": r["created_at"],
                "passed": r["passed"],
                "n_evaluated": r["n_evaluated"],
                "summary": r["summary"],
            }
        )
    (run_dir / "index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")
    (run_dir / "README.md").write_text(render_index_md(reports, slugs), encoding="utf-8")
    return paths
