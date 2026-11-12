"""Inference profiling: wall time vs image size, and energy / CO2 via codecarbon.

Per sample we record the model's inference time and the image size, plus the energy and
emissions of that call. The summary adds time buckets by image size so latency scaling
is visible. Caveat: codecarbon measures the machine running `ocr-eval`. For a local model
that is the model; for the API backend it only sees the client, not the server.
"""

import logging
import time
from contextlib import contextmanager
from dataclasses import dataclass
from statistics import mean

from pydantic import BaseModel

log = logging.getLogger("ocr_eval")

# (label, upper bound in megapixels)
SIZE_BUCKETS = [("<1MP", 1.0), ("1-4MP", 4.0), (">=4MP", float("inf"))]


class ProfilingConfig(BaseModel):
    codecarbon: bool = True
    country_iso_code: str = "FRA"  # offline tracker: no network call, grid mix from this country
    measure_power_secs: float = 1.0


@dataclass
class Measure:
    inference_s: float = 0.0
    energy_kwh: float | None = None
    emissions_kg: float | None = None


def image_stats(width: int, height: int) -> dict[str, float]:
    return {"width": width, "height": height, "megapixels": width * height / 1e6}


class Profiler:
    def __init__(self, cfg: ProfilingConfig, run_name: str):
        self.cfg = cfg
        self._tracker = None
        if cfg.codecarbon:
            from codecarbon import OfflineEmissionsTracker  # lazy: optional at runtime

            self._tracker = OfflineEmissionsTracker(
                project_name=run_name,
                country_iso_code=cfg.country_iso_code,
                measure_power_secs=cfg.measure_power_secs,
                save_to_file=False,
                log_level="error",
            )

    def __enter__(self):
        if self._tracker:
            self._tracker.start()
            # codecarbon swallows its own init errors; a dead tracker must not break the run.
            if not hasattr(self._tracker, "_start_time"):
                log.warning("codecarbon failed to start, energy metrics disabled")
                self._tracker = None
        return self

    def __exit__(self, *exc):
        if self._tracker:
            self.total = self._tracker.stop()  # kg CO2eq for the whole run
        return False

    @contextmanager
    def measure(self, name: str):
        m = Measure()
        if self._tracker:
            self._tracker.start_task(name)
        start = time.perf_counter()
        try:
            yield m
        finally:
            m.inference_s = time.perf_counter() - start
            if self._tracker:
                data = self._tracker.stop_task(name)
                if data is not None:
                    m.energy_kwh = data.energy_consumed
                    m.emissions_kg = data.emissions

    def run_totals(self) -> dict:
        t = getattr(self, "total", None)
        return {"emissions_kg_total": t} if t is not None else {}


def percentile(sorted_values: list[float], q: float) -> float:
    """Linear-interpolated percentile (same as numpy's default), q in [0, 100]."""
    if not sorted_values:
        raise ValueError("percentile of empty data")
    pos = (len(sorted_values) - 1) * q / 100
    lo = int(pos)
    hi = min(lo + 1, len(sorted_values) - 1)
    return sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * (pos - lo)


def summarize(samples: list[dict]) -> dict:
    """Aggregate per-sample `profile` dicts into run-level numbers and size buckets."""
    rows = [s["profile"] for s in samples if "profile" in s]
    if not rows:
        return {}
    times = sorted(r["inference_s"] for r in rows)
    out: dict = {
        "inference_s_mean": mean(times),
        "inference_s_p50": percentile(times, 50),
        "inference_s_p90": percentile(times, 90),
        "inference_s_p95": percentile(times, 95),
        "inference_s_p99": percentile(times, 99),
        "inference_s_max": times[-1],
        "s_per_megapixel": sum(times) / max(sum(r["megapixels"] for r in rows), 1e-9),
    }
    energies = [r["energy_kwh"] for r in rows if r.get("energy_kwh") is not None]
    if energies:
        out["energy_kwh_total"] = sum(energies)
        out["energy_kwh_mean"] = mean(energies)
        out["emissions_kg_samples"] = sum(
            r["emissions_kg"] for r in rows if r.get("emissions_kg") is not None
        )
    buckets, lo = {}, 0.0
    for label, hi in SIZE_BUCKETS:
        sel = [r for r in rows if lo <= r["megapixels"] < hi]
        if sel:
            buckets[label] = {
                "n": len(sel),
                "inference_s_mean": mean(r["inference_s"] for r in sel),
                "inference_s_p95": percentile(sorted(r["inference_s"] for r in sel), 95),
            }
        lo = hi
    out["by_image_size"] = buckets
    return out
