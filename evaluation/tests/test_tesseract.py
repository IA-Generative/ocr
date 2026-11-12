import shutil

import pytest
from PIL import Image, ImageDraw, ImageFont

from ocr_eval.dataset import Sample
from ocr_eval.models.tesseract import TesseractModel


class FakeTess:
    class Output:
        DICT = "dict"

    @staticmethod
    def image_to_data(image, lang, config, output_type):
        assert lang == "fra" and "--psm 3" in config and "--oem 1" in config
        return {
            # block / line rows have conf -1 and empty text; "  " is blank noise
            "text": ["", "Bonjour", "  ", "monde", "bruit"],
            "conf": ["-1", "96.5", "80", "91", "12"],
            "left": [0, 10, 0, 100, 200],
            "top": [0, 20, 0, 20, 20],
            "width": [500, 80, 5, 60, 30],
            "height": [50, 30, 5, 30, 30],
        }


def test_boxes_become_pixel_xyxy_and_layout_rows_are_dropped():
    model = TesseractModel({"min_conf": 50})
    model._tess = FakeTess
    pred = model.predict(Sample("1", Image.new("RGB", (600, 100))))
    assert pred.text == "Bonjour monde"  # layout row, blank and low-confidence word dropped
    assert pred.words[0].bbox == [10.0, 20.0, 90.0, 50.0]


def test_fingerprint_changes_with_language():
    assert (
        TesseractModel({"lang": "fra"}).fingerprint()["params"]["lang"]
        != TesseractModel({"lang": "fra+eng"}).fingerprint()["params"]["lang"]
    )


@pytest.mark.skipif(shutil.which("tesseract") is None, reason="tesseract not installed")
def test_real_tesseract_reads_french():
    pytest.importorskip("pytesseract")
    font = ImageFont.load_default(size=40)
    img = Image.new("RGB", (700, 100), "white")
    ImageDraw.Draw(img).text((20, 25), "Bonjour le monde", fill="black", font=font)
    with TesseractModel({"lang": "fra", "psm": 7}) as model:
        pred = model.predict(Sample("1", img))
    assert "Bonjour" in pred.text and pred.words[0].bbox is not None
