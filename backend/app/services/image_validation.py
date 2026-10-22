"""Offline semantic image screening, independent of disease softmax scores."""
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import threading

import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[3] / 'models' / 'validation'
_LOCK = threading.Lock()


class ValidatorUnavailable(RuntimeError):
    pass


@lru_cache(maxsize=1)
def _validator():
    try:
        import onnxruntime as ort
        metadata = json.loads((ROOT / 'metadata.json').read_text())
        for name, expected in metadata['sha256'].items():
            if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
                raise ValueError('Validator artifact hash mismatch')
        text = json.loads((ROOT / 'text_embeddings.json').read_text())
        options = ort.SessionOptions()
        options.intra_op_num_threads = 1
        options.inter_op_num_threads = 1
        options.enable_cpu_mem_arena = False
        session = ort.InferenceSession(str(ROOT / 'vision_model_quantized.onnx'), sess_options=options, providers=['CPUExecutionProvider'])
        return session, np.asarray(text['embeddings'], dtype=np.float32), text['positive_count']
    except Exception as exc:
        raise ValidatorUnavailable('Leaf image validation is unavailable. Try again after the service is configured.') from exc


def validator_available() -> bool:
    try:
        _validator()
        return True
    except ValidatorUnavailable:
        return False


def _pixels(image):
    image = ImageOps.exif_transpose(image).convert('RGB')
    width, height = image.size
    scale = 224 / min(width, height)
    image = image.resize((int(width * scale), int(height * scale)), Image.Resampling.BICUBIC)
    left, top = (image.width - 224) // 2, (image.height - 224) // 2
    image = image.crop((left, top, left + 224, top + 224))
    pixels = np.asarray(image, dtype=np.float32) / 255
    pixels = (pixels - np.array([.48145466, .4578275, .40821073], dtype=np.float32)) / np.array([.26862954, .26130258, .27577711], dtype=np.float32)
    return pixels.transpose(2, 0, 1)[None].copy()


def validate_leaf_candidate(image: Image.Image) -> str | None:
    if min(image.size) < 64:
        return 'Upload a clear leaf photo at least 64 pixels wide and high.'
    preview = image.copy()
    preview.thumbnail((256, 256))
    if float(np.asarray(preview, dtype=np.float32).std()) < 8:
        return 'The image has too little detail. Upload a clear supported leaf photo.'
    session, text_vectors, positive_count = _validator()
    try:
        with _LOCK:
            vector = session.run(['image_embeds'], {'pixel_values': _pixels(image)})[0][0]
    except Exception as exc:
        raise ValidatorUnavailable('Leaf image validation failed. Try again later.') from exc
    norm = np.linalg.norm(vector)
    if not np.isfinite(norm) or norm <= 0:
        raise ValidatorUnavailable('Leaf image validation failed. Try again later.')
    similarities = text_vectors @ (vector / norm)
    positive = float(np.max(similarities[:positive_count]))
    negative = float(np.max(similarities[positive_count:]))
    if positive < .24 or positive - negative < .025:
        return 'This image cannot be confirmed as a supported leaf photo. Upload a close-up tomato, potato, or bell pepper leaf without people, animals, vehicles or other objects.'
    return None
