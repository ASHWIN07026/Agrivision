"""Half-pixel bilinear resize with triangle antialiasing, matching TF resize semantics."""
import numpy as np


def _weights(source_size: int, output_size: int) -> np.ndarray:
    scale = np.float32(source_size / output_size)
    width = max(scale, np.float32(1.0))
    centers = (np.arange(output_size, dtype=np.float32) + np.float32(0.5)) * scale - np.float32(0.5)
    distance = np.abs(centers[:, None] - np.arange(source_size, dtype=np.float32)[None, :])
    weights = np.maximum(np.float32(0), np.float32(1) - distance / width)
    return weights / weights.sum(axis=1, keepdims=True)


def resize_rgb(image: np.ndarray, height: int, width: int) -> np.ndarray:
    image = np.asarray(image, dtype=np.float32)
    vertical = _weights(image.shape[0], height)
    horizontal = _weights(image.shape[1], width)
    partial = np.einsum('yh,hwc->ywc', vertical, image, optimize=True)
    return np.einsum('xw,ywc->yxc', horizontal, partial, optimize=True).astype(np.float32)
