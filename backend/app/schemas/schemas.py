"""
Pydantic schemas for request / response validation.
"""
from pydantic import BaseModel
from typing import Optional

class YieldRequest(BaseModel):
    crop: str
    soil_quality: float
    rainfall: float
    temperature: float

class YieldResponse(BaseModel):
    expected_yield_kg_per_hectare: float

class DiseaseResponse(BaseModel):
    disease: str
    confidence: float
    treatment: str

class MarketResponse(BaseModel):
    crop: str
    current_price: str
    trend: str
    demand: str
    region: Optional[str] = None
