from time import perf_counter
from typing import Union

import numpy as np
from paddleocr import TableRecognitionPipelineV2
from PIL import Image

from business.layout.configs.layout import LayoutSettings
from business.layout.utils.image import crop_normalized
from business.layout.utils.table import build_table_content
from services.base.model import BaseModelPrediction
from src.logger import logger
from src.schemas.output import Page


class TableStructureModel(BaseModelPrediction):
    """Reconnaît la structure des tables détectées (``page.tables``) et leur texte.

    L'OCR embarqué du pipeline ne tourne que sur le crop des tables, indépendamment de l'OCR
    principal. La détection de layout interne est désactivée : le crop *est* la table.
    """

    def __init__(self, settings: LayoutSettings | None = None):
        super().__init__()
        self.settings = settings or LayoutSettings()
        self.pipeline = TableRecognitionPipelineV2(
            device=self.settings.DEVICE,
            use_ocr_model=True,
            use_layout_detection=False,
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            cpu_threads=self.settings.CPU_THREADS,
            enable_mkldnn=self.settings.ENABLE_MKLDNN,
        )
        logger.info("[Table] pipeline loaded")

    def batch_predict(
        self,
        images: list[Union[np.ndarray, Image.Image]],
        pages: list[Page] = [],
        *args,
        **kwargs,
    ) -> list[Page]:
        assert len(images) == len(pages)
        for page, image in zip(pages, images):
            width, height = image.size
            for table_layout in page.tables:
                crop, (offset_x, offset_y) = crop_normalized(image.convert("RGB"), table_layout.coordinate)
                if crop.width < 2 or crop.height < 2:
                    continue
                t = perf_counter()
                results = list(self.pipeline.predict(np.array(crop)))
                logger.debug(f"[Table] crop {crop.size} in {perf_counter() - t:.2f}s")
                if not results or not results[0]["table_res_list"]:
                    continue
                table_res = results[0]["table_res_list"][0]
                cell_boxes = self._normalized_cell_boxes(
                    table_res.get("cell_box_list"), offset_x, offset_y, width, height
                )
                table_layout.table = build_table_content(table_res["pred_html"], cell_boxes=cell_boxes)
        return pages

    @staticmethod
    def _normalized_cell_boxes(raw_boxes, offset_x: int, offset_y: int, width: int, height: int):
        if raw_boxes is None or len(raw_boxes) == 0:
            return None
        return [
            [
                (xmin + offset_x) / width,
                (ymin + offset_y) / height,
                (xmax + offset_x) / width,
                (ymax + offset_y) / height,
            ]
            for xmin, ymin, xmax, ymax in raw_boxes
        ]
