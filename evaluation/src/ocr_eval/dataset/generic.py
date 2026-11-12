"""Column-driven adapter: works for any dataset described by the config columns."""

from typing import Any, ClassVar

from ocr_eval.dataset.base import DatasetAdapter, Sample, Word, normalize_bbox


class GenericAdapter(DatasetAdapter):
    name: ClassVar[str] = "generic"
    # Subclasses override these to preset a known schema; the config still wins when set.
    default_image_column: ClassVar[str] = "image"
    default_text_column: ClassVar[str] = "text"
    default_bboxes_column: ClassVar[str | None] = None
    default_bbox_format: ClassVar[str] = "xyxy"
    default_bbox_scale: ClassVar[str] = "pixel"

    def _opt(self, key: str, default: Any) -> Any:
        # Only fields explicitly set in the YAML override the adapter's defaults.
        return getattr(self.cfg, key) if key in self.cfg.model_fields_set else default

    def to_sample(self, row: dict[str, Any], index: int) -> Sample:
        image = row[self._opt("image_column", self.default_image_column)].convert("RGB")
        texts = row[self._opt("text_column", self.default_text_column)]
        bbox_col = self._opt("bboxes_column", self.default_bboxes_column)
        raw_boxes = row[bbox_col] if bbox_col else None

        if not isinstance(texts, (list, tuple)):  # plain transcription, no per-word boxes
            words = [Word(str(texts))]
        else:
            if raw_boxes is not None and len(raw_boxes) != len(texts):
                raise ValueError(f"{len(texts)} words but {len(raw_boxes)} bboxes")
            fmt = self._opt("bbox_format", self.default_bbox_format)
            scale = self._opt("bbox_scale", self.default_bbox_scale)
            words = [
                Word(
                    str(t),
                    normalize_bbox(raw_boxes[i], fmt, scale, *image.size)
                    if raw_boxes is not None
                    else None,
                )
                for i, t in enumerate(texts)
            ]
        return Sample(id=str(row.get("id", index)), image=image, words=words)
