"""Read the measured disease evaluation from a verified local training run."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "disease" / "disease_mobilenetv2.keras"
METADATA_PATH = PROJECT_ROOT / "models" / "disease" / "disease_metadata.json"
METRICS_PATH = PROJECT_ROOT / "reports" / "disease" / "evaluation_metrics.json"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as model_file:
        for block in iter(lambda: model_file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def evaluate() -> dict:
    if not METADATA_PATH.is_file() or not MODEL_PATH.is_file() or not METRICS_PATH.is_file():
        raise FileNotFoundError("No completed, verified disease training evaluation is available.")
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    if metadata.get("status") != "verified_trained":
        raise ValueError("Disease metadata does not identify a verified training run.")
    if metadata.get("model_sha256") != _sha256_file(MODEL_PATH):
        raise ValueError("Disease model hash does not match its training metadata.")
    return json.loads(METRICS_PATH.read_text(encoding="utf-8"))


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2))
