# AgriVision local demo

## Start the services

Open two PowerShell terminals in `D:\AgriVision`.

**Terminal 1 — FastAPI**

```powershell
Set-Location D:\AgriVision\backend
& ..\.venv\Scripts\python.exe -m uvicorn app.main:app --host localhost --port 8000
```

**Terminal 2 — React/Vite**

```powershell
Set-Location D:\AgriVision\frontend
npm run dev -- --host localhost --port 5173
```

Open `http://localhost:5173`. The backend docs are at
`http://localhost:8000/docs`; health and verified model status are at
`http://localhost:8000/api/health`.

The Python environment is the project-local `.venv`. If restoring it from
scratch, create the virtual environment first, then install the pinned
dependencies:

```powershell
Set-Location D:\AgriVision
py -3.13 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

The frontend uses its existing `package-lock.json`:

```powershell
Set-Location D:\AgriVision\frontend
npm ci
```

## Short HOD demonstration

1. Point out the header's local model IDs and the explicit unavailability of
   live market data.
2. In **Disease Detection**, upload a JPG or PNG. The verified classifier
   supports 15 Tomato, Potato, and Bell pepper PlantVillage categories. Explain
   that the score is not test accuracy and that controlled PlantVillage test
   metrics do not establish field-photo performance.
3. In **Yield Estimation**, select a FAOSTAT country/region, crop, and a year
   from 2012–2016. Explain that the output is in kg/hectare and uses historical
   country/region and crop data, not weather or soil.
4. In **Market Data**, show “Live market data unavailable”; no price or demand
   is fabricated when an authorized provider is not configured.
5. Refer to `RESULTS.md` and `reports/` for measured metrics, split strategy,
   per-class scores, confusion matrix, yield plot, and example screenshots.

Saved browser evidence:

- `reports/screenshots/disease_prediction.png`
- `reports/screenshots/yield_prediction.png`
- `reports/screenshots/market_unavailable.png`
- `reports/screenshots/invalid_image_error.png`

To rerun model training from the downloaded public datasets:

```powershell
Set-Location D:\AgriVision
& .\.venv\Scripts\python.exe ml\disease\train_disease_model.py --max-per-class 250 --epochs 12
& .\.venv\Scripts\python.exe ml\yield\train_yield_model.py
```

Disease training uses MobileNetV2 and CPU on the tested college computer; an
individual epoch took roughly 1–1.5 minutes. Training downloads ImageNet
MobileNetV2 weights if they are not already cached. Completed inference does
not need Internet access.
