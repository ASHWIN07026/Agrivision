"""Inference helper using the verified FAOSTAT yield pipeline and saved schema."""

from __future__ import annotations

import math
import time

import pandas as pd

from app.services.yield_year_policy import year_policy, estimate_context
from app.ml.model_loader import get_yield_metadata, get_yield_model


def predict_yield(country: str, crop: str, year: int) -> dict:
    model = get_yield_model()
    metadata = get_yield_metadata()
    if model is None:
        return {
            "status": "not_trained",
            "message": "Model not trained",
            "expected_yield_kg_per_hectare": None,
        }
    if country not in metadata["supported_countries"] or crop not in metadata["supported_crops"]:
        return {
            "status": "error",
            "message": "Country or crop is not supported by the trained model.",
            "expected_yield_kg_per_hectare": None,
        }

    minimum_year, maximum_year = year_policy(metadata)["accepted_prediction_year_range"]
    if not minimum_year <= int(year) <= maximum_year:
        return {
            "status": "error",
            "message": f"Year must be between {minimum_year} and {maximum_year}.",
            "expected_yield_kg_per_hectare": None,
        }

    inputs = pd.DataFrame(
        [{"country": country, "crop": crop, "year": int(year)}],
        columns=metadata["input_columns"],
    )
    start = time.perf_counter()
    prediction = float(model.predict(inputs)[0])
    if not math.isfinite(prediction):
        return {
            "status": "error",
            "message": "Yield model returned a non-finite result.",
            "expected_yield_kg_per_hectare": None,
        }
    return {
        "status": "ok",
        **estimate_context(metadata, int(year)),
        "country": country,
        "crop": crop,
        "year": int(year),
        "expected_yield_kg_per_hectare": round(prediction, 2),
        "units": "kg/hectare",
        "model_id": metadata["model_id"],
        "inference_ms": (time.perf_counter() - start) * 1000.0,
    }
