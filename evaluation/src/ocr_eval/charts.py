"""SVG charts for the models comparison, in a light and a dark variant.

Models are rows (labelled on the axis), never colors: with a handful of models identity by
color would break the "one color per entity" rule and the categorical palette cap. Color only
separates measures: CER vs WER (two categorical slots), latency percentiles (one-hue ordinal
ramp), a single measure (one hue). All palettes were checked with the dataviz validator
(scripts/validate_palette.js) against both chart surfaces.

Output is deterministic (fixed hash salt, no date, text kept as text), so an unchanged input
rewrites byte-identical files and creates no git diff.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, NullFormatter

THEMES = {
    "light": {
        "surface": "#fcfcfb",
        "ink": "#0b0b0b",
        "ink2": "#52514e",
        "muted": "#898781",
        "grid": "#e1e0d9",
        "axis": "#c3c2b7",
        "cer": "#2a78d6",
        "wer": "#eb6834",
        "ramp": ["#86b6ef", "#5598e7", "#256abf", "#104281"],  # blue 250 -> 650
        "single": "#2a78d6",
    },
    "dark": {
        "surface": "#1a1a19",
        "ink": "#f0efec",
        "ink2": "#c3c2b7",
        "muted": "#898781",
        "grid": "#2c2c2a",
        "axis": "#383835",
        "cer": "#3987e5",
        "wer": "#d95926",
        "ramp": ["#184f95", "#256abf", "#3987e5", "#6da7ec"],  # blue 600 -> 300
        "single": "#3987e5",
    },
}
PERCENTILES = ("p50", "p90", "p95", "p99")
WIDTH = 7.2


def _setup() -> None:
    plt.rcParams.update(
        {
            "svg.fonttype": "none",
            "svg.hashsalt": "ocr-eval",
            "font.family": "sans-serif",
            "font.sans-serif": ["system-ui", "Segoe UI", "Helvetica", "Arial", "DejaVu Sans"],
            "font.size": 9,
        }
    )


def _style(ax, t: dict, grid_axis: str) -> None:
    ax.set_facecolor(t["surface"])
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(t["axis"])
    ax.tick_params(colors=t["muted"], length=0)
    ax.grid(axis=grid_axis, color=t["grid"], linewidth=0.8)
    ax.set_axisbelow(True)


def _save(fig, path: Path, t: dict) -> None:
    fig.patch.set_facecolor(t["surface"])
    fig.savefig(
        path,
        format="svg",
        facecolor=t["surface"],
        metadata={"Date": None, "Creator": "ocr-eval", "Title": path.stem},
    )
    plt.close(fig)


def _grouped_bars(path, t, title, xlabel, models, series, colors, labels, xmax=None):
    """Horizontal grouped bars: one row per model, one bar per series."""
    _setup()
    n, k = len(models), len(series)
    fig, ax = plt.subplots(figsize=(WIDTH, 0.42 * n * max(1, k * 0.55) + 1.5))
    group = 0.78
    bar = group / k
    for j, values in enumerate(series):
        ys = [i - group / 2 + bar * (j + 0.5) for i in range(n)]
        # 2px surface-colored edge = the gap between adjacent bars
        ax.barh(
            ys,
            values,
            height=bar,
            color=colors[j],
            edgecolor=t["surface"],
            linewidth=1.5,
            label=labels[j],
        )
    ax.set_yticks(range(n), models, color=t["ink2"])
    ax.invert_yaxis()
    ax.set_xlabel(xlabel, color=t["ink2"])
    ax.set_xlim(0, xmax or max(max(s) for s in series) * 1.08 or 1)
    ax.set_title(title, loc="left", color=t["ink"], fontsize=10, fontweight="bold", pad=10)
    _style(ax, t, "x")
    if k > 1:
        leg = ax.legend(loc="lower right", frameon=False, ncol=k, fontsize=8)
        for text in leg.get_texts():
            text.set_color(t["ink2"])
    fig.tight_layout()
    _save(fig, path, t)


def quality(path, theme, title, rows):
    """rows: [(model, cer, wer)]"""
    t = THEMES[theme]
    _grouped_bars(
        path,
        t,
        title,
        "error rate (character / word)",
        [r[0] for r in rows],
        [[r[1] for r in rows], [r[2] for r in rows]],
        [t["cer"], t["wer"]],
        ["CER", "WER"],
    )


def latency(path, theme, title, rows):
    """rows: [(model, p50, p90, p95, p99)] in seconds"""
    t = THEMES[theme]
    _grouped_bars(
        path,
        t,
        title,
        "inference time per sample (s)",
        [r[0] for r in rows],
        [[r[i + 1] for r in rows] for i in range(4)],
        t["ramp"],
        list(PERCENTILES),
    )


def energy(path, theme, title, rows):
    """rows: [(model, mWh per sample)]"""
    t = THEMES[theme]
    _grouped_bars(
        path,
        t,
        title,
        "energy per sample (mWh, estimated)",
        [r[0] for r in rows],
        [[r[1] for r in rows]],
        [t["single"]],
        ["energy"],
    )


def quality_vs_time(path, theme, panels):
    """panels: {dataset title: [(model, mean inference s, cer)]}. One panel per dataset, points
    labelled directly (identity by label, not by color)."""
    _setup()
    t = THEMES[theme]
    fig, axes = plt.subplots(len(panels), 1, figsize=(WIDTH, 3.1 * len(panels)), squeeze=False)
    for ax, (title, pts) in zip(axes[:, 0], panels.items()):
        for model, x, y in pts:
            ax.scatter(
                [x], [y], s=46, color=t["single"], edgecolor=t["surface"], linewidth=1.5, zorder=3
            )
            ax.annotate(
                model,
                (x, y),
                xytext=(6, 5),
                textcoords="offset points",
                fontsize=7.5,
                color=t["ink2"],
            )
        ax.set_xscale("log")
        ax.xaxis.set_major_formatter(FormatStrFormatter("%g"))  # 0.1, 1, 10 not 10^-1
        ax.xaxis.set_minor_formatter(NullFormatter())
        ax.set_xlabel("mean inference time per sample (s, log scale)", color=t["ink2"])
        ax.set_ylabel("CER", color=t["ink2"])
        ax.set_title(title, loc="left", color=t["ink"], fontsize=10, fontweight="bold", pad=8)
        ax.margins(x=0.18, y=0.2)
        _style(ax, t, "both")
    fig.tight_layout()
    _save(fig, path, t)
