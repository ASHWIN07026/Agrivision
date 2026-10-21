from fastapi import APIRouter
from app.services.market_service import get_market_price

router = APIRouter(prefix="/api/market", tags=["Market Intelligence"])

@router.get("/price")
def market_price(crop: str, region: str = "India"):
    return get_market_price(crop, region)
