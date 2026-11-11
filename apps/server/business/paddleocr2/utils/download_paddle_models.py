import argparse
import os


def parameters():
    parser = argparse.ArgumentParser(description="Choix de version et de folder.")
    parser.add_argument(
        "--folder",
        required=False,
        default=None,
        help="Folder to download/cache the models into.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parameters()

    if args.folder:
        os.environ["PADDLE_PDX_CACHE_HOME"] = args.folder

    from business.paddleocr2.configs.paddle import PaddleSetting

    paddle_settings = PaddleSetting()
    folder = args.folder or paddle_settings.PADDLE_OCR_BASE_DIR

    from paddleocr import PaddleOCR
    from business.paddleocr2.configs.paddle import build_paddle_ocr_kwargs

    print(
        f"Downloading PaddleOCR models {paddle_settings.TEXT_DETECTION_MODEL_NAME} / "
        f"{paddle_settings.TEXT_RECOGNITION_MODEL_NAME} ({paddle_settings.OCR_ENGINE}) into {folder}..."
    )
    PaddleOCR(
        use_textline_orientation=False,
        use_doc_unwarping=False,
        **{**build_paddle_ocr_kwargs(paddle_settings), "device": "cpu"},
    )
