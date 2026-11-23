import json
import os

import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE, "model")
KERAS_PATH = os.path.join(MODEL_DIR, "leaf_model.keras")
TFLITE_PATH = os.path.join(MODEL_DIR, "leaf_model.tflite")
CLASSES_PATH = os.path.join(MODEL_DIR, "class_names.json")


def model_files_present() -> bool:
    return os.path.exists(CLASSES_PATH) and (
        os.path.exists(KERAS_PATH) or os.path.exists(TFLITE_PATH)
    )


def load_class_names():
    with open(CLASSES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


class Predictor:
    """Wraps either the .keras model or the .tflite model behind one predict()."""

    def __init__(self):
        import tensorflow as tf

        self.class_names = load_class_names()
        if os.path.exists(KERAS_PATH):
            self.model = tf.keras.models.load_model(KERAS_PATH)
            self.kind = "keras"
        else:
            with open(TFLITE_PATH, "rb") as f:
                header = f.read(8)
            if len(header) < 8 or header[4:8] != b"TFL3":
                raise RuntimeError("leaf_model.tflite is not a valid TensorFlow Lite model")
            self.interp = tf.lite.Interpreter(model_path=TFLITE_PATH)
            self.interp.allocate_tensors()
            self.inp = self.interp.get_input_details()[0]
            self.out = self.interp.get_output_details()[0]
            self.kind = "tflite"

    def predict(self, batch: np.ndarray) -> np.ndarray:
        if self.kind == "keras":
            probs = self.model.predict(batch, verbose=0)[0]
        else:
            self.interp.set_tensor(self.inp["index"], batch.astype(self.inp["dtype"]))
            self.interp.invoke()
            probs = self.interp.get_tensor(self.out["index"])[0]
        return np.asarray(probs, dtype=np.float32)

    def top_k(self, batch: np.ndarray, k: int = 3):
        probs = self.predict(batch)
        idx = np.argsort(probs)[::-1][:k]
        return [(self.class_names[i], float(probs[i])) for i in idx]


def pretty(label: str):
    """'Tomato___Late_blight' -> ('Tomato', 'Late blight')"""
    parts = label.split("___")
    crop = parts[0].replace("_", " ").replace(",", "").strip()
    disease = (parts[1] if len(parts) > 1 else "").replace("_", " ").strip()
    return crop, disease
