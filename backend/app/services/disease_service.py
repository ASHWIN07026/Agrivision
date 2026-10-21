"""Inference helper using the verified model's saved input shape and classes."""

from __future__ import annotations

import io
import time

import numpy as np
import tensorflow as tf
from PIL import Image, UnidentifiedImageError

from app.ml.model_loader import get_disease_classes, get_disease_metadata, get_disease_model

MAX_IMAGE_BYTES = 10 * 1024 * 1024


async def predict_disease_from_image(file) -> dict:
    model = get_disease_model()
    if model is None:
        return {
            "status": "not_trained",
            "message": "Model not trained",
            "disease": "Model not trained",
            "confidence": None,
        }

    image_bytes = await file.read(MAX_IMAGE_BYTES + 1)
    if not image_bytes:
        return {"status": "error", "message": "Upload a non-empty leaf image."}
    if len(image_bytes) > MAX_IMAGE_BYTES:
        return {"status": "error", "message": "Image exceeds the 10 MB limit."}
    try:
        with Image.open(io.BytesIO(image_bytes)) as image:
            if image.format not in {"JPEG", "PNG"}:
                raise ValueError("Only JPG and PNG images are supported.")
            image.verify()
        height, width, _ = get_disease_metadata().get("input_shape", [160, 160, 3])
        image_tensor = tf.io.decode_image(image_bytes, channels=3, expand_animations=False)
        image_tensor.set_shape((None, None, 3))
        array = tf.image.resize(
            image_tensor, (int(height), int(width)), antialias=True
        ).numpy()
    except (UnidentifiedImageError, OSError, ValueError):
        return {"status": "error", "message": "Unsupported or corrupt image. Upload a valid JPG or PNG."}

    start = time.perf_counter()
    probabilities = model.predict(np.expand_dims(array, axis=0), verbose=0)[0]
    class_names = get_disease_classes()
    if len(probabilities) != len(class_names):
        return {"status": "error", "message": "Model output does not match its saved class mapping."}
    index = int(np.argmax(probabilities))
    return {
        "status": "ok",
        "disease": class_names[index],
        "confidence": float(probabilities[index]),
        "confidence_kind": "softmax score; not test accuracy",
        "model_id": get_disease_metadata().get("model_id"),
        "inference_ms": (time.perf_counter() - start) * 1000.0,
        "guidance": "This classifier returns a PlantVillage label, not a treatment prescription. Confirm diagnosis with a local agricultural extension service.",
    }
