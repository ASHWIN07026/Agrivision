# AgriVision

Plant disease classification and historical crop-yield estimation.

## Live application
https://agrivision-6o2f.onrender.com

## Features
- React dashboard connected to FastAPI.
- MobileNetV2 disease classification for 15 supported PlantVillage classes.
- Random Forest historical yield estimation using country/region, crop and year.
- Lightweight LiteRT disease inference for deployment.

## Evaluation
- Original disease model test accuracy: 83.45% on 731 images.
- Yield model test R²: 0.657.
- Converted LiteRT model checked on three sample images; full test-set evaluation remains pending.

## Limitations
- Yield interface currently supports 2012–2016; future forecasting is not verified.
- Live market data is unavailable.
- Field-photo performance and database connectivity remain unverified.
- Disease classification does not provide a treatment prescription.

## Repository contents
Application source, models and supporting reports are packaged in
AgriVision_Render_Free.zip. The root Dockerfile extracts this archive
and builds the frontend and backend.
