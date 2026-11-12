import json

import pytest
from PIL import Image

from ocr_eval import report as report_mod
from ocr_eval import runner
from ocr_eval.config import RunConfig
from ocr_eval.dataset import Sample, Word
from ocr_eval.models import MODELS, Model, Prediction


class EchoModel(Model):
    """Local stand-in: returns the reference, proving no API is needed."""

    name = "echo"

    def predict(self, sample):
        return Prediction(text=sample.reference)


def test_runs_with_local_model(monkeypatch):
    monkeypatch.setitem(MODELS, "echo", EchoModel)
    monkeypatch.setattr(
        runner,
        "load_samples",
        lambda cfg: iter([Sample("1", Image.new("RGB", (4, 4)), [Word("hello"), Word("world")])]),
    )
    cfg = RunConfig.model_validate(
        {
            "name": "t",
            "model": {"type": "echo", "device": "cpu"},
            "datasets": [{"name": "x"}],
            "thresholds": {"cer_max": 0.1},
        }
    )
    assert cfg.model.params == {"device": "cpu"}
    [report] = runner.run(cfg)
    assert report["passed"] and report["summary"]["cer"] == 0.0


def test_report_has_profiling(monkeypatch):
    monkeypatch.setitem(MODELS, "echo", EchoModel)
    imgs = [Image.new("RGB", (100, 100)), Image.new("RGB", (2000, 2000))]
    monkeypatch.setattr(
        runner,
        "load_samples",
        lambda cfg: iter([Sample(str(i), im, [Word("a")]) for i, im in enumerate(imgs)]),
    )
    cfg = RunConfig.model_validate(
        {
            "name": "t",
            "model": {"type": "echo"},
            "datasets": [{"name": "x"}],
            "profiling": {"codecarbon": False},
        }
    )
    prof = runner.run(cfg)[0]["profiling"]
    assert set(prof["by_image_size"]) == {"<1MP", ">=4MP"}
    assert prof["inference_s_mean"] >= 0


def test_hardware_metadata():
    from ocr_eval import hardware

    hw = hardware.collect(hardware.HardwareConfig(label="srv"))
    assert hw["label"] == "srv" and hw["cpu_cores_logical"] >= 1
    assert hw["accelerator"] in ("cpu", "gpu")


def test_one_report_per_dataset(monkeypatch, tmp_path):
    monkeypatch.setitem(MODELS, "echo", EchoModel)
    monkeypatch.setattr(
        runner,
        "load_samples",
        lambda ds: iter([Sample("1", Image.new("RGB", (4, 4)), [Word(ds.name)])]),
    )
    cfg = RunConfig.model_validate(
        {
            "name": "multi",
            "model": {"type": "echo"},
            "datasets": [{"name": "org/a"}, {"name": "org/b", "split": "validation"}],
            "profiling": {"codecarbon": False},
        }
    )
    reports = runner.run(cfg)
    paths = report_mod.write_reports(reports, tmp_path)
    assert [p.name for p in paths] == ["org_a__test", "org_b__validation"]
    assert (paths[0] / "report.json").exists() and (paths[0] / "README.md").exists()
    assert (tmp_path / "multi" / "index.json").exists()


class CountingModel(EchoModel):
    name = "counting"
    calls = 0

    def fingerprint(self):
        return {"type": "counting"}

    def predict(self, sample):
        CountingModel.calls += 1
        return super().predict(sample)


def _cached_cfg(**ds):
    return RunConfig.model_validate(
        {
            "name": "c",
            "model": {"type": "counting"},
            "datasets": [{"name": "org/a", **ds}],
            "profiling": {"codecarbon": False},
        }
    )


def test_unchanged_run_is_not_rerun(monkeypatch, tmp_path):
    monkeypatch.setitem(MODELS, "counting", CountingModel)
    monkeypatch.setattr(runner.cache, "dataset_revision", lambda ds: "rev1")
    monkeypatch.setattr(
        runner,
        "load_samples",
        lambda ds: iter([Sample("1", Image.new("RGB", (4, 4)), [Word("hi")])]),
    )
    CountingModel.calls = 0

    first = runner.run(_cached_cfg(), tmp_path)
    report_mod.write_reports(first, tmp_path)
    second = runner.run(_cached_cfg(), tmp_path)
    assert CountingModel.calls == 1 and second[0]["_cached"]
    assert second[0]["created_at"] == first[0]["created_at"]
    assert second[0]["summary"] == first[0]["summary"]

    # --force, a new dataset revision, or a changed dataset config all re-run
    runner.run(_cached_cfg(), tmp_path, force=True)
    assert CountingModel.calls == 2
    monkeypatch.setattr(runner.cache, "dataset_revision", lambda ds: "rev2")
    runner.run(_cached_cfg(), tmp_path)
    assert CountingModel.calls == 3
    runner.run(_cached_cfg(max_samples=5), tmp_path)
    assert CountingModel.calls == 4


def test_api_model_is_never_cached(monkeypatch, tmp_path):
    from ocr_eval.models.api import ApiModel

    assert ApiModel({}).fingerprint() is None


def test_readme_is_human_readable(monkeypatch, tmp_path):
    monkeypatch.setitem(MODELS, "counting", CountingModel)
    monkeypatch.setattr(runner.cache, "dataset_revision", lambda ds: "abc")
    monkeypatch.setattr(
        runner,
        "load_samples",
        lambda ds: iter([Sample("1", Image.new("RGB", (4, 4)), [Word("a|b")])]),
    )
    [path] = report_mod.write_reports(runner.run(_cached_cfg(), tmp_path), tmp_path)
    text = (path / "README.md").read_text()
    for needle in ("**Date:**", "## Scores", "| cer |", "## Hardware", "Worst samples", "a\\|b"):
        assert needle in text, needle


def test_percentiles_are_interpolated():
    from ocr_eval.profiling import percentile

    data = [float(i) for i in range(1, 101)]  # 1..100
    assert percentile(data, 50) == 50.5
    assert percentile(data, 90) == pytest.approx(90.1)
    assert percentile(data, 99) == pytest.approx(99.01)
    assert percentile([3.0], 99) == 3.0


def test_report_has_all_percentiles_and_keeps_samples_out_of_json(monkeypatch, tmp_path):
    monkeypatch.setitem(MODELS, "counting", CountingModel)
    monkeypatch.setattr(runner.cache, "dataset_revision", lambda ds: "r")
    monkeypatch.setattr(
        runner,
        "load_samples",
        lambda ds: iter(
            [Sample(str(i), Image.new("RGB", (4, 4)), [Word("hi")]) for i in range(30)]
        ),
    )
    reports = runner.run(_cached_cfg(), tmp_path)
    prof = reports[0]["profiling"]
    assert prof["inference_s_p50"] <= prof["inference_s_p90"] <= prof["inference_s_p99"]
    assert {"inference_s_p95", "inference_s_max"} <= set(prof)

    [path] = report_mod.write_reports(reports, tmp_path)
    data = json.loads((path / "report.json").read_text())
    assert "samples" not in data and len(data["worst_samples"]) == 5
    assert len((path / "samples.jsonl").read_text().splitlines()) == 30
    assert "p50 / p90 / p95 / p99" in (path / "README.md").read_text()

    # A cached rerun must not erase the per-sample dump nor change a single byte of the report.
    before = (path / "report.json").read_bytes(), (path / "README.md").read_bytes()
    report_mod.write_reports(runner.run(_cached_cfg(), tmp_path), tmp_path)
    assert before == ((path / "report.json").read_bytes(), (path / "README.md").read_bytes())
    assert (path / "samples.jsonl").exists()


def test_hardware_label_makes_cache_independent_of_cpu(monkeypatch):
    from ocr_eval import cache

    cfg, ds = _cached_cfg(), _cached_cfg().datasets[0]

    def hw(cpu):
        return {"label": "ci", "cpu_model": cpu, "accelerator": "cpu", "gpus": []}

    def fp(h):
        return cache.fingerprint(cfg, ds, {"type": "m"}, h, "r")

    assert fp(hw("AMD EPYC")) == fp(hw("Intel Xeon"))
    assert fp({**hw("a"), "label": None}) != fp({**hw("b"), "label": None})
