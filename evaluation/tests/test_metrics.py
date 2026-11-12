from ocr_eval.metrics import cer, wer


def test_identical_is_zero():
    assert cer("Hello  World", "hello world") == 0.0
    assert wer("Hello  World", "hello world") == 0.0


def test_one_wrong_word():
    assert wer("a b c d", "a b x d") == 0.25


def test_empty_reference():
    assert cer("", "") == 0.0
    assert cer("", "x") == 1.0
