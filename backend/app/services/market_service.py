"""Market lookup fails closed until a verified authorized provider is integrated."""


def get_market_price(crop: str, region: str = "India") -> dict:
    return {
        "status": "unavailable",
        "message": "Live market data unavailable: no verified authorized market API integration is configured.",
        "crop": crop,
        "region": region,
        "current_price": None,
        "trend": None,
        "demand": None,
        "source": None,
        "units": None,
        "updated_at": None,
    }
