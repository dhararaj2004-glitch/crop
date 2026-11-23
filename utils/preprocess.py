import numpy as np
from PIL import Image, ImageOps

IMG_SIZE = (224, 224)


def load_image(file_or_path) -> np.ndarray:
    """Open an uploaded file / path as an RGB uint8 array (EXIF rotation fixed)."""
    img = Image.open(file_or_path)
    img = ImageOps.exif_transpose(img).convert("RGB")
    return np.array(img)


def to_model_input(rgb: np.ndarray) -> np.ndarray:
    """Resize to 224x224 and add a batch dimension.

    Values stay in 0-255 float32: the MobileNetV2 preprocessing (scaling to [-1, 1])
    is already baked into the saved model by the training notebook.
    """
    img = Image.fromarray(rgb).resize(IMG_SIZE, Image.BILINEAR)
    return np.expand_dims(np.asarray(img, dtype=np.float32), axis=0)
