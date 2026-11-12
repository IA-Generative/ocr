"""Side-by-side comparison of every model's reports: tables and charts, no verdict.

Reads <reports_dir>/<model>/<dataset>/report.json and writes <reports_dir>/README.md plus the
SVG charts in <reports_dir>/charts/. Models are listed alphabetically, never ranked, and the
text states how the numbers were measured rather than what they mean. Output is deterministic
(no generation date): an unchanged set of reports produces no diff.
"""

import json
from collections import defaultdict
from pathlib import Path

from ocr_eval import charts

CHART_DIR = "charts"


def _mwh(kwh: float | None) -> float | None:
    return None if kwh is None else kwh * 1e6  # 1 kWh = 1e6 mWh


def load(reports_dir: Path) -> dict[str, dict[str, dict]]:
    """{dataset folder: {model name: report}}"""
    data: dict[str, dict[str, dict]] = defaultdict(dict)
    for path in sorted(reports_dir.glob("*/*/report.json")):
        report = json.loads(path.read_text(encoding="utf-8"))
        data[path.parent.name][report["name"]] = report
    return dict(sorted(data.items()))


def _f(value: float | None, spec: str) -> str:
    return "—" if value is None else format(value, spec)


def _title(report: dict) -> str:
    ds = report["dataset"]
    return f"{ds['name']} ({ds['split']})"


def _picture(name: str, alt: str) -> str:
    base = f"{CHART_DIR}/{name}"
    return (
        f'<picture>\n  <source media="(prefers-color-scheme: dark)" srcset="{base}.dark.svg">\n'
        f'  <img src="{base}.light.svg" alt="{alt}" width="720">\n</picture>\n'
    )


def _both(fn, out: Path, name: str, *args) -> None:
    for theme in ("light", "dark"):
        fn(out / f"{name}.{theme}.svg", theme, *args)


def build(reports_dir: str | Path) -> Path:
    reports_dir = Path(reports_dir)
    data = load(reports_dir)
    if not data:
        raise SystemExit(f"No report.json found under {reports_dir}/<model>/<dataset>/")
    out = reports_dir / CHART_DIR
    out.mkdir(parents=True, exist_ok=True)

    models: dict[str, dict] = {}
    for by_model in data.values():
        for name, r in by_model.items():
            models.setdefault(name, r)

    lines = [
        "# Models comparison",
        "",
        (
            f"{len(models)} models on {len(data)} datasets, from the reports under this folder. "
            "Models are listed alphabetically; nothing here is ranked or interpreted."
        ),
        "",
        "## Models",
        "",
        "| Model | Backend | Parameters | Hardware |",
        "|---|---|---|---|",
    ]
    for name in sorted(models):
        m = models[name]["model"]
        params = ", ".join(f"{k}={v}" for k, v in m.items() if k != "type")
        hw = models[name]["hardware"]
        where = hw["label"] or f"{hw['cpu_model']} ({hw['cpu_cores_logical']} threads)"
        lines.append(f"| [{name}]({name}/README.md) | `{m['type']}` | {params} | {where} |")

    lines += [
        "",
        "## How the numbers were measured",
        "",
        (
            "- **CER / WER**: character / word error rate against the dataset reference, after "
            "lowercasing and whitespace normalization. Both can exceed 1. They are sensitive to "
            "reading order (the reference order is the dataset's, not necessarily the page's)."
        ),
        (
            "- **Inference time**: wall time of the model call per sample, with p50 / p90 / p95 / p99 "
            "over the evaluated samples; **s/MP** is total time over total megapixels."
        ),
        (
            "- **Energy**: codecarbon estimate per sample (mWh) on the machine running the "
            "evaluation; an estimate when CPU power counters are not readable."
        ),
        (
            "- Times and energy are only comparable between reports measured on the same hardware "
            "(see the Hardware column). The reference of `lightonai/fc-amf-ocr` is docTR output, "
            "not a human transcription."
        ),
    ]

    scatter: dict[str, list] = {}
    for ds_dir, by_model in data.items():
        names = sorted(by_model)
        any_r = by_model[names[0]]
        title = _title(any_r)
        lines += ["", f"## {title}", ""]
        counts = {n: by_model[n]["n_evaluated"] for n in names}
        if len(set(counts.values())) > 1:
            lines += [
                (
                    "Not every model was evaluated on the same number of samples (see "
                    "Samples); the samples are drawn with the same seed."
                ),
                "",
            ]
        lines += [
            "| Model | Samples | CER | WER | Mean (s) | p50 | p90 | p95 | p99 | s/MP | mWh/sample | Date |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|",
        ]
        for n in names:
            r = by_model[n]
            s, p = r["summary"], r["profiling"]
            lines.append(
                f"| [{n}]({n}/{ds_dir}/README.md) | {r['n_evaluated']} | {_f(s.get('cer'), '.4f')} | {_f(s.get('wer'), '.4f')} "
                f"| {_f(p.get('inference_s_mean'), '.3f')} | {_f(p.get('inference_s_p50'), '.3f')} "
                f"| {_f(p.get('inference_s_p90'), '.3f')} | {_f(p.get('inference_s_p95'), '.3f')} "
                f"| {_f(p.get('inference_s_p99'), '.3f')} | {_f(p.get('s_per_megapixel'), '.3f')} "
                f"| {_f(_mwh(p.get('energy_kwh_mean')), '.2f')} | {r['created_at'][:10]} |"
            )

        q = [
            (n, by_model[n]["summary"]["cer"], by_model[n]["summary"]["wer"])
            for n in names
            if "cer" in by_model[n]["summary"]
        ]
        lat = [
            (n, *(by_model[n]["profiling"][f"inference_s_{k}"] for k in charts.PERCENTILES))
            for n in names
            if by_model[n]["profiling"]
        ]
        en = [
            (n, _mwh(by_model[n]["profiling"]["energy_kwh_mean"]))
            for n in names
            if by_model[n]["profiling"].get("energy_kwh_mean") is not None
        ]
        if q:
            _both(charts.quality, out, f"{ds_dir}.quality", f"{title}: error rates", q)
            lines += ["", _picture(f"{ds_dir}.quality", f"CER and WER per model on {title}")]
        if lat:
            _both(charts.latency, out, f"{ds_dir}.latency", f"{title}: inference time", lat)
            lines += [_picture(f"{ds_dir}.latency", f"Inference time percentiles on {title}")]
        if en:
            _both(charts.energy, out, f"{ds_dir}.energy", f"{title}: energy per sample", en)
            lines += [_picture(f"{ds_dir}.energy", f"Energy per sample on {title}")]
        scatter[title] = [
            (n, by_model[n]["profiling"]["inference_s_mean"], by_model[n]["summary"]["cer"])
            for n in names
            if by_model[n]["profiling"] and "cer" in by_model[n]["summary"]
        ]

    scatter = {k: v for k, v in scatter.items() if v}
    if scatter:
        _both(charts.quality_vs_time, out, "cer_vs_time", scatter)
        lines += [
            "",
            "## CER against inference time",
            "",
            _picture("cer_vs_time", "CER against mean inference time, per dataset"),
        ]

    readme = reports_dir / "README.md"
    readme.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return readme
