import io, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))
from fastapi.testclient import TestClient
from app.main import app
from PIL import Image

with TestClient(app) as client:
    ready = client.get("/api/ready")
    print("readiness", ready.status_code, ready.json())
    assert ready.status_code == 200
    root = client.get("/")
    assert root.status_code == 200 and "text/html" in root.headers["content-type"]
    print("dashboard static HTML PASS")
    result = client.post("/api/yield/predict", data={"country":"India", "crop":"Maize (corn)", "year":2016})
    assert result.status_code == 200
    print("yield", result.json())
    assert client.post("/api/yield/predict", data={"country":"India", "crop":"Wheat", "year":2026}).json()["estimate_type"] == "experimental"
    assert client.post("/api/disease/predict", files={"file":("bad.txt", b"invalid", "text/plain")}).status_code == 400
    samples = list((Path(__file__).resolve().parent / "samples").rglob("*.JPG"))
    samples += list((Path(__file__).resolve().parent / "samples").rglob("*.jpg"))
    if samples:
        result = client.post("/api/disease/predict",files={"file":(samples[0].name,samples[0].read_bytes(),"image/jpeg")})
        assert result.status_code == 200
        print("disease", result.json())
    else:
        print("No sample leaf image found; disease prediction not checked")
    assert client.get("/api/market/price?crop=Wheat").json()["status"] == "unavailable"
    print("invalid image, experimental future year acceptance and market unavailable PASS")
