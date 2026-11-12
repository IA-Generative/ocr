"""Dataset loading: HF datasets with heterogeneous schemas, normalized to `Sample`."""

from collections.abc import Iterator

from ocr_eval.config import DatasetConfig
from ocr_eval.dataset.base import DatasetAdapter, Sample, Word, normalize_bbox
from ocr_eval.dataset.fc_amf import FcAmfAdapter
from ocr_eval.dataset.funsd import FunsdAdapter
from ocr_eval.dataset.generic import GenericAdapter
from ocr_eval.dataset.rimes import RimesAdapter

# Register new dataset schemas here.
ADAPTERS: dict[str, type[DatasetAdapter]] = {
    a.name: a for a in (GenericAdapter, FunsdAdapter, RimesAdapter, FcAmfAdapter)
}


def load_samples(cfg: DatasetConfig) -> Iterator[Sample]:
    if cfg.adapter not in ADAPTERS:
        raise ValueError(f"Unknown adapter {cfg.adapter!r}, available: {sorted(ADAPTERS)}")
    adapter = ADAPTERS[cfg.adapter](cfg)

    from datasets import load_dataset  # heavy import, keep it lazy

    if cfg.streaming:
        ds = load_dataset(cfg.name, cfg.config, split=cfg.split, streaming=True)
        ds = ds.shuffle(seed=cfg.seed, buffer_size=cfg.shuffle_buffer)
    else:
        ds = load_dataset(cfg.name, cfg.config, split=cfg.split).shuffle(seed=cfg.seed)
        if cfg.max_samples is not None:
            ds = ds.select(range(min(cfg.max_samples, len(ds))))

    count = 0
    for i, row in enumerate(ds):
        for sample in adapter.iter_samples(row, i):
            yield sample
            count += 1
            if cfg.max_samples is not None and count >= cfg.max_samples:
                return


__all__ = ["ADAPTERS", "DatasetAdapter", "Sample", "Word", "load_samples", "normalize_bbox"]
