import json

from ocr_eval import compare


def _report(name, cer, wer, mean, n=10, kwh=1e-5):
    return {
        "name": name,
        "created_at": "2026-11-12T10:00:00+00:00",
        "n_evaluated": n,
        "dataset": {"name": "org/ds", "split": "test"},
        "model": {"type": "tesseract", "lang": "fra"},
        "hardware": {"label": "ci", "cpu_model": "x", "cpu_cores_logical": 4},
        "summary": {"cer": cer, "wer": wer},
        "profiling": {
            "inference_s_mean": mean,
            "inference_s_p50": mean,
            "inference_s_p90": mean * 1.5,
            "inference_s_p95": mean * 2,
            "inference_s_p99": mean * 3,
            "s_per_megapixel": 1.0,
            "energy_kwh_mean": kwh,
        },
    }


def _write(root, reports):
    for r in reports:
        d = root / r["name"] / "org_ds__test"
        d.mkdir(parents=True)
        (d / "report.json").write_text(json.dumps(r))


def test_comparison_lists_every_model_without_ranking(tmp_path):
    _write(tmp_path, [_report("b-model", 0.2, 0.3, 0.5), _report("a-model", 0.9, 1.1, 0.1, n=5)])
    text = compare.build(tmp_path).read_text()
    assert text.index("a-model") < text.index("b-model")  # alphabetical, not by score
    for needle in ("| 0.2000 |", "| 1.1000 |", "10.00 |", "same number of samples", "charts/"):
        assert needle in text, needle
    # no verdict language
    for word in ("best", "worst", "winner", "recommend", "better", "faster", "should"):
        assert word not in text.lower(), word
    assert len(list((tmp_path / "charts").glob("*.svg"))) == 8  # 4 charts x light/dark


def test_comparison_is_byte_stable(tmp_path):
    _write(tmp_path, [_report("a", 0.2, 0.3, 0.5), _report("b", 0.4, 0.5, 0.2)])
    compare.build(tmp_path)
    first = {
        p.name: p.read_bytes() for p in [tmp_path / "README.md", *(tmp_path / "charts").glob("*")]
    }
    compare.build(tmp_path)
    second = {
        p.name: p.read_bytes() for p in [tmp_path / "README.md", *(tmp_path / "charts").glob("*")]
    }
    assert first == second
