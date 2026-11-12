import pytest
from PIL import Image

from ocr_eval.config import DatasetConfig
from ocr_eval.dataset import ADAPTERS, normalize_bbox


def row(**kw):
    return {"image": Image.new("RGB", (2000, 1000)), **kw}


def test_norm1000_to_pixels():
    assert normalize_bbox([100, 100, 500, 200], "xyxy", "norm1000", 2000, 1000) == [
        200,
        100,
        1000,
        200,
    ]


def test_xywh_to_xyxy():
    assert normalize_bbox([10, 20, 30, 40], "xywh", "pixel", 100, 100) == [10, 20, 40, 60]


def test_funsd_preset_scales_boxes():
    adapter = ADAPTERS["funsd"](DatasetConfig(name="x"))
    s = adapter.to_sample(
        row(tokens=["a", "b"], bboxes=[[0, 0, 500, 500], [500, 0, 1000, 1000]]), 0
    )
    assert s.reference == "a b"
    assert s.words[1].bbox == [1000, 0, 2000, 1000]


def test_generic_plain_string_has_no_bbox():
    adapter = ADAPTERS["generic"](DatasetConfig(name="x"))
    s = adapter.to_sample(row(text="hello world"), 3)
    assert s.id == "3" and s.reference == "hello world" and s.bboxes == []


def test_config_overrides_adapter_defaults():
    cfg = DatasetConfig(name="x", bbox_scale="pixel")
    s = ADAPTERS["funsd"](cfg).to_sample(row(tokens=["a"], bboxes=[[1, 2, 3, 4]]), 0)
    assert s.words[0].bbox == [1, 2, 3, 4]


def test_misaligned_raises():
    with pytest.raises(ValueError):
        ADAPTERS["funsd"](DatasetConfig(name="x")).to_sample(
            row(tokens=["a", "b"], bboxes=[[0, 0, 1, 1]]), 0
        )


def _fc_row(n_pages=3):
    import pymupdf

    doc = pymupdf.open()
    for i in range(n_pages):
        doc.new_page(width=200, height=100).insert_text((10, 50), f"page {i}")
    word = {"value": "hi", "confidence": 0.9, "geometry": [[0.1, 0.2], [0.5, 0.6]]}
    pages = [
        {
            "page_idx": i,
            "dimensions": [200, 400],
            "blocks": [{"geometry": [], "lines": [{"geometry": [], "words": [word]}]}]
            if i != 1
            else [],  # blank page
        }
        for i in range(n_pages)
    ]
    return {"__key__": "doc1", "pdf": doc.tobytes(), "json.gz": {"pages": pages}}


def test_fc_amf_renders_pages_with_matching_boxes():
    cfg = DatasetConfig(name="x", adapter="fc_amf", pages_per_document=5)
    samples = list(ADAPTERS["fc_amf"](cfg).iter_samples(_fc_row(), 0))
    assert sorted(s.id for s in samples) == ["doc1#p0", "doc1#p2"]  # blank page skipped
    s = samples[0]
    assert s.image.size == (400, 200)  # 200x100pt at 144 DPI
    assert s.words[0].bbox == [40.0, 40.0, 200.0, 120.0]  # normalized -> pixels


def test_fc_amf_page_choice_is_deterministic():
    cfg = DatasetConfig(name="x", adapter="fc_amf", pages_per_document=1)

    def pick():
        return [s.id for s in ADAPTERS["fc_amf"](cfg).iter_samples(_fc_row(10), 0)]

    assert pick() == pick()
