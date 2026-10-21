from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

from app.services.disease_service import predict_disease_from_image

router = APIRouter(prefix="/api/disease", tags=["Disease Detection"])

@router.post("/predict")
async def disease_predict(file: UploadFile = File(...)):
    result = await predict_disease_from_image(file)
    status_code = 503 if result["status"] == "not_trained" else 400 if result["status"] == "error" else 200
    return JSONResponse(status_code=status_code, content=result)
