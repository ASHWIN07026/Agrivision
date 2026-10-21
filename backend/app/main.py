"""Local FastAPI endpoints for verified AgriVision model inference."""

from __future__ import annotations

import io
import math
import os
from pathlib import Path
import time

import numpy as np
import pandas as pd
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image, UnidentifiedImageError
from app.ml.image_preprocessing import resize_rgb

from app.ml.model_loader import (
    get_disease_classes,
    get_disease_metadata,
    get_disease_model,
    get_yield_metadata,
    get_yield_model,
    model_status,
)
from app.services.market_service import get_market_price
from app.services.yield_year_policy import year_policy, estimate_context

app = FastAPI(title="AgriVision API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if origin.strip()],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

MAX_IMAGE_BYTES = 10 * 1024 * 1024


def _disease_not_trained() -> dict:
    return {
        "status": "not_trained",
        "message": "Model not trained",
        "disease": "Model not trained",
        "confidence": None,
        "guidance": "A verified PlantVillage model artifact is unavailable.",
    }


def _yield_not_trained() -> dict:
    return {
        "status": "not_trained",
        "message": "Model not trained",
        "expected_yield_kg_per_hectare": None,
    }


@app.get("/api/health")
def health_check() -> dict:
    status = model_status()
    return {
        "status": "ok",
        "source": "verified local training artifacts",
        **status,
        "models": {
            "disease": "trained" if get_disease_model() is not None else "missing",
            "yield": "trained" if get_yield_model() is not None else "missing",
        },
    }


@app.get("/api/yield/options")
def yield_options():
    model = get_yield_model()
    metadata = get_yield_metadata()
    if model is None:
        return JSONResponse(status_code=503, content=_yield_not_trained())
    return {
        "status": "ok",
        "model_id": metadata["model_id"],
        "countries": metadata["supported_countries"],
        "crops": metadata["supported_crops"],
        "recommended_prediction_year_range": metadata["recommended_prediction_year_range"],
        **year_policy(metadata),
        "target_units": metadata["target_units"],
    }


@app.post("/api/disease/predict")
async def predict_disease(file: UploadFile = File(...)):
    model = get_disease_model()
    if model is None:
        return JSONResponse(status_code=503, content=_disease_not_trained())

    image_bytes = await file.read(MAX_IMAGE_BYTES + 1)
    if not image_bytes:
        return JSONResponse(status_code=400, content={"status": "error", "message": "Upload a non-empty leaf image."})
    if len(image_bytes) > MAX_IMAGE_BYTES:
        return JSONResponse(status_code=413, content={"status": "error", "message": "Image exceeds the 10 MB limit."})

    try:
        with Image.open(io.BytesIO(image_bytes)) as source:
            if source.format not in {"JPEG", "PNG"}:
                raise ValueError("Only JPG and PNG images are supported.")
            source.verify()
        input_shape = get_disease_metadata().get("input_shape", [160, 160, 3])
        height, width = int(input_shape[0]), int(input_shape[1])
        with Image.open(io.BytesIO(image_bytes)) as source:
            if source.width * source.height > 4_000_000:
                return JSONResponse(status_code=413, content={"status": "error", "message": "Resize the image to at most 4 megapixels."})
            image_array = resize_rgb(np.asarray(source.convert("RGB")), height, width)
    except (UnidentifiedImageError, OSError, ValueError):
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Unsupported or corrupt image. Upload a valid JPG or PNG."},
        )

    start = time.perf_counter()
    try:
        probabilities = model.predict(np.expand_dims(image_array, axis=0), verbose=0)[0]
    except Exception as exc:
        print(f"[api] Disease inference failed: {exc}")
        return JSONResponse(status_code=500, content={"status": "error", "message": "Disease inference failed."})
    inference_ms = (time.perf_counter() - start) * 1000.0
    class_names = get_disease_classes()
    if len(probabilities) != len(class_names):
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Model output does not match its saved class mapping."},
        )
    predicted_index = int(np.argmax(probabilities))
    disease = class_names[predicted_index]
    return {
        "status": "ok",
        "disease": disease,
        "confidence": float(probabilities[predicted_index]),
        "confidence_kind": "softmax score; not test accuracy",
        "model_id": get_disease_metadata().get("model_id"),
        "inference_ms": inference_ms,
        "guidance": "This classifier returns a PlantVillage label, not a treatment prescription. Confirm diagnosis with a local agricultural extension service.",
    }


@app.post("/api/yield/predict")
def predict_yield(
    country: str = Form(..., min_length=1),
    crop: str = Form(..., min_length=1),
    year: int = Form(..., ge=1900, le=2100),
):
    model = get_yield_model()
    if model is None:
        return JSONResponse(status_code=503, content=_yield_not_trained())
    metadata = get_yield_metadata()
    if country not in metadata["supported_countries"]:
        return JSONResponse(
            status_code=422,
            content={"status": "error", "message": "Select a country or region listed in the model options."},
        )
    if crop not in metadata["supported_crops"]:
        return JSONResponse(
            status_code=422,
            content={"status": "error", "message": "Select a crop listed in the model options."},
        )
    minimum_year, maximum_year = year_policy(metadata)["accepted_prediction_year_range"]
    if not minimum_year <= year <= maximum_year:
        return JSONResponse(
            status_code=422,
            content={
                "status": "error",
                "message": f"Choose a year from {minimum_year} to {maximum_year}.",
            },
        )

    features = pd.DataFrame([{"country": country, "crop": crop, "year": year}], columns=metadata["input_columns"])
    start = time.perf_counter()
    try:
        prediction = float(model.predict(features)[0])
    except Exception as exc:
        print(f"[api] Yield inference failed: {exc}")
        return JSONResponse(status_code=500, content={"status": "error", "message": "Yield inference failed."})
    inference_ms = (time.perf_counter() - start) * 1000.0
    if not math.isfinite(prediction):
        return JSONResponse(status_code=500, content={"status": "error", "message": "Yield model returned a non-finite result."})
    return {
        "status": "ok",
        "country": country,
        "crop": crop,
        "year": year,
        "expected_yield_kg_per_hectare": round(prediction, 2),
        "units": "kg/hectare",
        "model_id": metadata["model_id"],
        "inference_ms": inference_ms,
        **estimate_context(metadata, year),
    }


@app.get("/api/market/price")
def market_price(crop: str, region: str = "India") -> dict:
    return get_market_price(crop=crop, region=region)


@app.get("/api/ready")
def readiness_check():
    status = model_status()
    ready = status["disease_model_available"] and status["yield_model_available"]
    return JSONResponse(status_code=200 if ready else 503, content={"ready": ready, **status})


# Register after API routes. A built frontend shares the API origin.
FRONTEND_DIST = Path(__file__).resolve().parents[1] / "static"
if (FRONTEND_DIST / "index.html").is_file():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="dashboard")
