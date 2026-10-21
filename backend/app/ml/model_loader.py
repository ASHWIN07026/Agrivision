"""Load only model artifacts produced by the verified local training pipelines."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DISEASE_MODEL_PATH = PROJECT_ROOT / "models" / "disease" / "disease_mobilenetv2.keras"
DISEASE_METADATA_PATH = PROJECT_ROOT / "models" / "disease" / "disease_metadata.json"
YIELD_MODEL_PATH = PROJECT_ROOT / "models" / "yield" / "faostat_random_forest_yield.joblib"
YIELD_METADATA_PATH = PROJECT_ROOT / "models" / "yield" / "yield_metadata.json"

_disease_model = None
_yield_model = None
_disease_metadata: dict = {}
_yield_metadata: dict = {}
_disease_classes: list[str] = []
_load_errors: dict[str, str] = {}


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_verified_metadata(metadata_path: Path, model_path: Path) -> dict:
    if not metadata_path.is_file() or not model_path.is_file():
        raise FileNotFoundError("Verified model artifact or its metadata is missing.")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("status") != "verified_trained":
        raise ValueError("Model metadata does not identify a verified training run.")
    if metadata.get("model_sha256") != _sha256_file(model_path):
        raise ValueError("Model artifact hash does not match its training metadata.")
    expected_path = model_path.relative_to(PROJECT_ROOT).as_posix()
    if metadata.get("model_path") != expected_path:
        raise ValueError("Model metadata references an unexpected artifact path.")
    return metadata


try:
    _disease_metadata = _read_verified_metadata(DISEASE_METADATA_PATH, DISEASE_MODEL_PATH)
    _disease_classes = _disease_metadata.get("class_names", [])
    mapping = _disease_metadata.get("class_mapping", {})
    if not _disease_classes or _disease_classes != list(mapping.values()):
        raise ValueError("Disease metadata has no valid ordered class mapping.")
    from app.ml.lite_model import LiteDiseaseModel
    conversion = json.loads((PROJECT_ROOT / "models/disease/disease_lite_metadata.json").read_text())
    lite_path = PROJECT_ROOT / conversion["model_path"]
    if conversion["source_model_sha256"] != _disease_metadata["model_sha256"]:
        raise ValueError("LiteRT model source does not match original training artifact.")
    if _sha256_file(lite_path) != conversion["model_sha256"]:
        raise ValueError("LiteRT artifact hash does not match conversion metadata.")
    _disease_model = LiteDiseaseModel(lite_path)
    _disease_metadata = {**_disease_metadata, "original_model_id": _disease_metadata["model_id"], "model_id": conversion["model_id"], "runtime": "LiteRT float32", "runtime_validation": conversion["validation_scope"]}
    if int(_disease_model.output_shape[-1]) != len(_disease_classes):
        raise ValueError("Disease model output does not match its saved class mapping.")
except Exception as exc:  # Keep the API available while making the missing artifact explicit.
    _load_errors["disease"] = str(exc)
    _disease_model = None
    _disease_classes = []
    print(f"[model_loader] Disease model unavailable: {exc}")

try:
    _yield_metadata = _read_verified_metadata(YIELD_METADATA_PATH, YIELD_MODEL_PATH)
    import joblib

    _yield_model = joblib.load(YIELD_MODEL_PATH)
    if not hasattr(_yield_model, "predict") or not hasattr(_yield_model, "named_steps"):
        raise TypeError("Verified yield artifact is not a scikit-learn prediction pipeline.")
except Exception as exc:  # Keep the API available while making the missing artifact explicit.
    _load_errors["yield"] = str(exc)
    _yield_model = None
    print(f"[model_loader] Yield model unavailable: {exc}")


def get_disease_model():
    return _disease_model


def get_yield_model():
    return _yield_model


def get_disease_classes() -> list[str]:
    return _disease_classes


def get_disease_metadata() -> dict:
    return _disease_metadata


def get_yield_metadata() -> dict:
    return _yield_metadata


def model_status() -> dict:
    return {
        "disease_model_available": _disease_model is not None,
        "yield_model_available": _yield_model is not None,
        "disease_model_id": _disease_metadata.get("model_id"),
        "yield_model_id": _yield_metadata.get("model_id"),
        "disease_supported_categories": _disease_classes,
        "market_data_available": False,
        "market_message": "Live market data unavailable: no verified authorized market API integration is configured.",
        "model_load_errors": _load_errors,
    }
