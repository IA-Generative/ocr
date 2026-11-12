"""Hardware / environment metadata, so a report says what the numbers were measured on.

This describes the machine running `ocr-eval`. For the API backend that is only the client:
describe the server with `hardware.label` in the config (e.g. "api: 1x A100, 32 vCPU").
"""

import os
import platform
import sys
from importlib import metadata

import psutil
from pydantic import BaseModel


class HardwareConfig(BaseModel):
    label: str | None = None  # free text, e.g. the server the API backend runs on


def _cpu_model() -> str:
    try:
        with open("/proc/cpuinfo", encoding="utf-8") as f:
            for line in f:
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or platform.machine()


def _gpus() -> list[dict]:
    try:
        import pynvml  # shipped with codecarbon; absent/unusable on machines without NVIDIA

        pynvml.nvmlInit()
        try:
            gpus = []
            for i in range(pynvml.nvmlDeviceGetCount()):
                h = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(h)
                gpus.append(
                    {
                        "name": name.decode() if isinstance(name, bytes) else name,
                        "memory_gb": round(pynvml.nvmlDeviceGetMemoryInfo(h).total / 1024**3, 1),
                    }
                )
            return gpus
        finally:
            pynvml.nvmlShutdown()
    except Exception:  # noqa: BLE001 - no driver / no GPU is a normal case
        return []


def _pkg_version(name: str) -> str | None:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None


def collect(cfg: HardwareConfig | None = None) -> dict:
    gpus = _gpus()
    return {
        # CI sets OCR_EVAL_HARDWARE_LABEL so runner-class timings share one stable identity.
        "label": os.environ.get("OCR_EVAL_HARDWARE_LABEL") or (cfg.label if cfg else None),
        "cpu_model": _cpu_model(),
        "cpu_cores_physical": psutil.cpu_count(logical=False),
        "cpu_cores_logical": psutil.cpu_count(logical=True),
        "ram_gb": round(psutil.virtual_memory().total / 1024**3, 1),
        "gpus": gpus,
        "accelerator": "gpu" if gpus else "cpu",
        "os": platform.platform(),
        "python": sys.version.split()[0],
        "in_ci": bool(os.environ.get("CI")),
        "in_container": os.path.exists("/.dockerenv"),
        "libs": {
            n: _pkg_version(n) for n in ("torch", "onnxruntime", "paddlepaddle", "transformers")
        }
        | {"codecarbon": _pkg_version("codecarbon")},
    }
