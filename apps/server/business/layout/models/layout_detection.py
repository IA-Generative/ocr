from time import time
from typing import Union

import numpy as np
from paddleocr import LayoutDetection
from PIL import Image

from business.layout.configs.layout import LayoutSettings
from services.base.model import BaseModelPrediction
from src.logger import logger
from src.schemas.layout import Layout
from src.schemas.output import Page

TABLE_LABELS = frozenset({"table"})
IMAGE_LABELS = frozenset({"image", "chart", "seal", "header_image", "footer_image"})
FORMULA_LABELS = frozenset({"formula"})


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


class LayoutDetectionModel(BaseModelPrediction):
    """Détecte les zones de la page et alimente ``layouts``, ``images`` et ``formulas``.

    Les images et les formules sont conservées en bbox seule (pas de reconnaissance de formule).
    Les tables sont structurées par ``TableStructureModel`` dans un second temps.
    """

    def __init__(self, settings: LayoutSettings | None = None):
        super().__init__()
        self.settings = settings or LayoutSettings()
        self.model = LayoutDetection(
            model_name=self.settings.LAYOUT_MODEL_NAME,
            device=self.settings.DEVICE,
            layout_nms=True,
            threshold=self.settings.LAYOUT_SCORE_THRESHOLD,
            cpu_threads=self.settings.CPU_THREADS,
            enable_mkldnn=self.settings.ENABLE_MKLDNN,
        )
        logger.info(f"[Layout] model {self.settings.LAYOUT_MODEL_NAME} loaded")

    def batch_predict(
        self,
        images: list[Union[np.ndarray, Image.Image]],
        pages: list[Page] = [],
        *args,
        **kwargs,
    ) -> list[Page]:
        if len(pages):
            assert len(images) == len(pages)
        else:
            pages = [Page(page=i) for i in range(len(images))]

        t = time()
        predictions = self.model.predict(
            [np.array(image.convert("RGB")) for image in images],
            batch_size=self.settings.LAYOUT_BATCH_SIZE,
        )
        logger.debug(f"[Layout] {len(images)} image(s) in {time() - t:.2f}s")

        for page, image, prediction in zip(pages, images, predictions):
            width, height = image.size
            page.layouts, page.images, page.formulas, page.tables = [], [], [], []
            for box in prediction["boxes"]:
                xmin, ymin, xmax, ymax = box["coordinate"]
                layout = Layout(
                    cls_id=int(box["cls_id"]),
                    label=box["label"],
                    score=float(box["score"]),
                    coordinate=[
                        clamp01(xmin / width),
                        clamp01(ymin / height),
                        clamp01(xmax / width),
                        clamp01(ymax / height),
                    ],
                )
                page.layouts.append(layout)
                if layout.label in IMAGE_LABELS:
                    page.images.append(layout.model_copy())
                elif layout.label in FORMULA_LABELS:
                    page.formulas.append(layout.model_copy())
                elif layout.label in TABLE_LABELS:
                    page.tables.append(layout.model_copy())
        return pages
