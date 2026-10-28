"""Télécharge au build les modèles du worker layout (layout + pipeline de tables) dans le cache PaddleX."""

import argparse
import os


def parameters():
    parser = argparse.ArgumentParser(description="Téléchargement des modèles layout.")
    parser.add_argument("--folder", required=False, default=None, help="PaddleX cache folder.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parameters()
    if args.folder:
        os.environ["PADDLE_PDX_CACHE_HOME"] = args.folder

    from business.layout.configs.layout import LayoutSettings

    settings = LayoutSettings(DEVICE="cpu")

    from paddleocr import LayoutDetection, TableRecognitionPipelineV2

    print(f"Downloading layout model {settings.LAYOUT_MODEL_NAME}...")
    LayoutDetection(model_name=settings.LAYOUT_MODEL_NAME, device="cpu")

    print("Downloading table recognition pipeline models...")
    TableRecognitionPipelineV2(
        device="cpu",
        use_ocr_model=True,
        use_layout_detection=False,
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
    )
