"""
Utility helpers shared across the AgriVision backend.
"""
import json, base64, io

def image_bytes_to_base64(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")

def parse_json_safe(text: str) -> dict:
    try:
        return json.loads(text)
    except Exception:
        return {}

def clamp(value: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, value))
