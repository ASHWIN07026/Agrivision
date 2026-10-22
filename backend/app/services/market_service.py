"""Server-side lookup of published AGMARKNET prices from data.gov.in."""

from __future__ import annotations

from datetime import date, datetime
import json
import logging
import math
import os
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


logger = logging.getLogger(__name__)
API_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
API_KEY_ENV = "DATA_GOV_IN_API_KEY"
SOURCE_NAME = "AGMARKNET via data.gov.in"
SOURCE_URL = "https://www.data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi"
REQUEST_TIMEOUT_SECONDS = 10
MAX_RESPONSE_BYTES = 2 * 1024 * 1024

COMMODITIES = {
    "tomato": "Tomato",
    "potato": "Potato",
    "pepper": "Capsicum",
    "bell pepper": "Capsicum",
    "rice": "Rice",
    "wheat": "Wheat",
    "onion": "Onion",
}


class MarketProviderError(Exception):
    def __init__(self, status_code: int, code: str, message: str):
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message


def _normalized_fields(record: dict) -> dict[str, object]:
    return {
        re.sub(r"[^a-z0-9]", "", str(key).lower()): value
        for key, value in record.items()
    }


def _field(fields: dict[str, object], *names: str) -> str | None:
    for name in names:
        value = fields.get(name)
        if value is not None and str(value).strip():
            return str(value).strip()
    return None


def _number(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        number = float(value.replace(",", ""))
    except ValueError:
        return None
    return number if math.isfinite(number) and number >= 0 else None


def _record_date_key(record: dict) -> date:
    value = record.get("arrival_date")
    for pattern in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(str(value), pattern).date()
        except (TypeError, ValueError):
            continue
    return date.min


def _format_record(record: dict) -> dict | None:
    fields = _normalized_fields(record)
    commodity = _field(fields, "commodity")
    state = _field(fields, "state")
    district = _field(fields, "district")
    market = _field(fields, "market")
    arrival_date = _field(fields, "arrivaldate")
    if not all((commodity, state, district, market, arrival_date)):
        return None

    prices = [_number(_field(fields, name, name + "rsquintal")) for name in ("minprice", "maxprice", "modalprice")]
    if any(value is None for value in prices):
        return None
    if not prices[0] <= prices[2] <= prices[1]:
        return None
    if _record_date_key({"arrival_date": arrival_date}) == date.min:
        return None

    return {
        "commodity": commodity,
        "variety": _field(fields, "variety"),
        "state": state,
        "district": district,
        "market": market,
        "arrival_date": arrival_date,
        "min_price": _number(_field(fields, "minprice", "minpricersquintal")),
        "max_price": _number(_field(fields, "maxprice", "maxpricersquintal")),
        "modal_price": _number(_field(fields, "modalprice", "modalpricersquintal")),
        "price_unit": "INR/quintal",
        "source": SOURCE_NAME,
        "source_url": SOURCE_URL,
        "freshness": "Published mandi observation; check its date; not real-time.",
    }


def get_market_price(
    crop: str,
    state: str | None = None,
    district: str | None = None,
    market: str | None = None,
    observed_date: str | None = None,
    region: str | None = None,
) -> dict:
    """Return recent official records; provider credentials never leave the backend."""
    commodity = COMMODITIES.get(crop.strip().lower())
    if commodity is None:
        raise MarketProviderError(
            422,
            "unsupported_crop",
            "Choose tomato, potato, bell pepper, rice, wheat, or onion.",
        )

    state = (state or "").strip()
    if not state and region and region.strip().lower() != "india":
        state = region.strip()

    date_filter = None
    if observed_date:
        try:
            date_filter = date.fromisoformat(observed_date).strftime("%d/%m/%Y")
        except ValueError as exc:
            raise MarketProviderError(
                422, "invalid_date", "Date must use the YYYY-MM-DD format."
            ) from exc

    api_key = os.environ.get(API_KEY_ENV, "").strip()
    if not api_key:
        raise MarketProviderError(
            503,
            "market_api_not_configured",
            f"Published market prices are not configured. Set {API_KEY_ENV} in the backend environment.",
        )

    params = [
        ("api-key", api_key),
        ("format", "json"),
        ("limit", "100"),
        ("sort[arrival_date]", "desc"),
        ("filters[commodity]", commodity),
    ]
    if state:
        params.append(("filters[state]", state))
    if district:
        params.append(("filters[district]", district.strip()))
    if market:
        params.append(("filters[market]", market.strip()))
    if date_filter:
        params.append(("filters[arrival_date]", date_filter))

    request = Request(
        f"{API_URL}?{urlencode(params)}",
        headers={"Accept": "application/json", "User-Agent": "AgriVision/1.0"},
    )
    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            payload_bytes = response.read(MAX_RESPONSE_BYTES + 1)
    except HTTPError as exc:
        if exc.code == 429:
            code, message = (
                "market_api_rate_limited",
                "The official market-data service is rate limiting requests. Try again later.",
            )
            status_code = 503
        elif exc.code in (401, 403):
            code, message = (
                "market_api_authentication_failed",
                f"The official market-data service rejected {API_KEY_ENV}. Verify its key and resource access.",
            )
            status_code = 503
        else:
            code, message = (
                "market_api_unavailable",
                "The official market-data service could not complete the request.",
            )
            status_code = 503
        logger.warning("Market provider returned HTTP %s.", exc.code)
        raise MarketProviderError(status_code, code, message) from exc
    except (TimeoutError, URLError) as exc:
        logger.warning("Market provider connection failed.")
        raise MarketProviderError(
            503,
            "market_api_unavailable",
            "The official market-data service could not be reached. Try again later.",
        ) from exc

    if len(payload_bytes) > MAX_RESPONSE_BYTES:
        raise MarketProviderError(
            502, "market_api_response_too_large", "The market-data response exceeded the allowed size."
        )
    try:
        payload = json.loads(payload_bytes)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise MarketProviderError(
            502, "market_api_invalid_response", "The market-data service returned an invalid response."
        ) from exc

    source_records = payload.get("records") if isinstance(payload, dict) else None
    if not isinstance(source_records, list):
        raise MarketProviderError(
            502, "market_api_invalid_response", "The market-data service response has no records list."
        )

    records = [
        formatted
        for source_record in source_records
        if isinstance(source_record, dict)
        if (formatted := _format_record(source_record)) is not None
    ]
    records.sort(key=_record_date_key, reverse=True)
    records = records[:10]

    if not records:
        return {
            "status": "not_found",
            "message": "No matching published market-price records were returned for these filters.",
            "crop": crop,
            "commodity": commodity,
            "records": [],
            "source": SOURCE_NAME,
            "freshness": "Published mandi observations; check their dates; not real-time.",
        }

    return {
        "status": "ok",
        "crop": crop,
        "commodity": commodity,
        "records": records,
        "source": SOURCE_NAME,
        "freshness": "Published mandi observations; check their dates; not real-time.",
    }
