from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from app.services.yield_service import predict_yield

router = APIRouter(prefix="/api/yield", tags=["Yield Prediction"])

@router.post("/predict")
async def yield_predict(
    country: str = Form(..., min_length=1),
    crop: str = Form(..., min_length=1),
    year: int = Form(..., ge=1900, le=2100),
):
    result = predict_yield(country, crop, year)
    status_code = 503 if result["status"] == "not_trained" else 422 if result["status"] == "error" else 200
    return JSONResponse(status_code=status_code, content=result)
