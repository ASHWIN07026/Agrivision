# AgriVision — Mini Project

AgriVision is an agriculture dashboard for plant disease classification and historical crop-yield estimation.

## Live Demo
https://agrivision-6o2f.onrender.com

## Project Modules
1. Disease Detection — classifies leaf images into 15 supported PlantVillage categories.
2. Yield Estimation — estimates historical crop yield using country/region, crop and year.
3. Market Information — interface available; live data integration remains pending.

## Technologies
- Frontend: React and Vite
- Backend: Python and FastAPI
- Disease Model: MobileNetV2
- Deployed Disease Runtime: LiteRT
- Yield Model: Random Forest Regressor
- Deployment: Docker on Render

## Datasets
- PlantVillage: leaf disease classification.
- FAOSTAT: historical country/region crop-yield records.

## Evaluation Results
| Model | Metric | Result |
|---|---|---|
| Original MobileNetV2 | Test accuracy | 83.45% |
| Original MobileNetV2 | Macro F1 | 83.47% |
| Random Forest | R² | 0.657 |
| Random Forest | MAE | 7,202.85 kg/ha |
| Random Forest | RMSE | 13,220.11 kg/ha |

Disease evaluation used 731 held-out images.
The converted LiteRT model was checked on three sample images;
full test-set evaluation of the converted model remains pending.

## Demonstrated Output
- Disease classification displayed through the dashboard.
- India / Maize (corn) / 2016: 5,949.99 kg/ha.

A disease prediction score is not the model's test accuracy.

## Limitations
- Disease detection covers the supported classes, not all plants or diseases.
- Current yield interface accepts years 2012–2016.
- Yield estimates are historical, not validated future forecasts.
- Live market information is unavailable.
- Field-photo performance and database connectivity remain unverified.
- The deployed website requires internet access.

## Repository Structure
- AgriVision_Render_Free.zip: source code, models and supporting reports.
- Dockerfile: extracts the archive and builds the application.
- LICENSE: project license.

## Academic Purpose
Developed as a college mini project to demonstrate machine
learning integration with a web dashboard.
