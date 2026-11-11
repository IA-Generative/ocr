from business.paddleocr2.configs.paddle import PaddleSetting, build_paddle_ocr_kwargs


def test_default_is_ppocrv6_tiny_onnx():
    kwargs = build_paddle_ocr_kwargs(PaddleSetting())
    assert kwargs["text_detection_model_name"] == "PP-OCRv6_tiny_det"
    assert kwargs["text_recognition_model_name"] == "PP-OCRv6_tiny_rec"
    assert kwargs["engine"] == "onnxruntime"
    assert kwargs["engine_config"] == {"intra_op_num_threads": PaddleSetting().CPU_THREADS}
    assert "cpu_threads" not in kwargs and "enable_mkldnn" not in kwargs


def test_paddle_engine_keeps_paddle_specific_options():
    kwargs = build_paddle_ocr_kwargs(PaddleSetting(OCR_ENGINE="paddle", CPU_THREADS=4, ENABLE_MKLDNN=True))
    assert kwargs["engine"] == "paddle"
    assert kwargs["cpu_threads"] == 4
    assert kwargs["enable_mkldnn"] is True
    assert "engine_config" not in kwargs
