from PIL import Image


def normalized_box_to_pixels(box: list[float], width: int, height: int) -> tuple[int, int, int, int]:
    xmin, ymin, xmax, ymax = box
    left = max(0, min(width, int(xmin * width)))
    right = max(0, min(width, int(xmax * width)))
    upper = max(0, min(height, int(ymin * height)))
    lower = max(0, min(height, int(ymax * height)))
    return left, upper, right, lower


def crop_normalized(image: Image.Image, box: list[float]) -> tuple[Image.Image, tuple[int, int]]:
    """Crop une boîte normalisée [0, 1] ; retourne aussi l'offset (x, y) du crop en pixels."""
    left, upper, right, lower = normalized_box_to_pixels(box, *image.size)
    return image.crop((left, upper, right, lower)), (left, upper)
