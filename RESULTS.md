# AgriVision verified results

Last verified: 7 October 2026

## Summary

AgriVision now runs two real, locally trained prediction models through the
React dashboard and FastAPI. Disease classification uses a 15-class
PlantVillage subset. Yield estimation uses historical FAOSTAT country/region,
crop, and year records. Both models are available without external services.
Market data is unavailable because no authorized live provider is configured.

Metrics below are from held-out evaluation data, not estimates or README
claims. PlantVillage results measure performance on held-out images from the
same controlled dataset; they do not establish field-photo performance.

## Disease classification

- **Source:** PlantVillage unaugmented archive from Mendeley Data,
  [DOI 10.17632/tywbtsjrjv.1](https://data.mendeley.com/datasets/tywbtsjrjv/1),
  distributed with a CC0 1.0 license.
- **Archive:** `data/raw/source_archives/plant_village_without_augmentation.zip`
  (868,032,562 bytes; SHA-256
  `ac3432453984d02a86197987e775a5429d0d59e7cc7c35bcf5a8f50349b90ff0`).
- **Subset:** 22,787 original images across 15 Tomato, Potato, and Bell pepper
  classes. The training run sampled 3,653 images (up to 250 per class, subject
  to available images and related-image groups).
- **Class counts in source subset:**

| Class | Images |
|---|---:|
| Pepper, bell — Bacterial spot | 997 |
| Pepper, bell — healthy | 1,478 |
| Potato — Early blight | 1,000 |
| Potato — Late blight | 1,000 |
| Potato — healthy | 152 |
| Tomato — Bacterial spot | 2,127 |
| Tomato — Early blight | 1,000 |
| Tomato — Late blight | 1,909 |
| Tomato — Leaf Mold | 952 |
| Tomato — Septoria leaf spot | 1,771 |
| Tomato — Spider mites, two-spotted spider mite | 1,676 |
| Tomato — Target Spot | 1,404 |
| Tomato — Yellow Leaf Curl Virus | 5,357 |
| Tomato — mosaic virus | 373 |
| Tomato — healthy | 1,591 |

- **Architecture:** MobileNetV2 with ImageNet pretrained weights and frozen
  backbone; global average pooling, dropout 0.3, and a 15-output softmax head.
  Input is 160x160 RGB in the 0..255 range, rescaled in-model to -1..1.
  Training-only augmentation: horizontal flip, rotation, zoom, and contrast.
- **Split:** exact SHA-256 and 64-bit perceptual-hash grouping (Hamming
  distance <= 4) before two-stage `StratifiedGroupKFold`, seed 42. Train:
  2,337; validation: 585; test: 731. No related-image group crossed splits.
  Early stopping selected weights by validation accuracy. The held-out test set
  was evaluated after training/model selection. Training ran 10 epochs; the
  selected checkpoint was from epoch 7 (validation accuracy 83.76%).
- **Measured test results (731 images):**

| Metric | Result |
|---|---:|
| Accuracy | 83.45% |
| Macro precision | 84.48% |
| Macro recall | 83.78% |
| Macro F1 | 83.47% |
| Warm API `model.predict` median (7 requests; first request excluded) | 92.26 ms/image |
| Cold first API `model.predict` request | 1,382.54 ms |
| Batched test-evaluation throughput average | 28.56 ms/image |

The timings are measured on this CPU and are not general hardware guarantees.
API model-predict timings exclude file decoding and image resizing; the
evaluation throughput is measured over the batched 731-image test pass and is
not directly comparable to a single-image HTTP request.

- **Test set caveat:** PlantVillage images have controlled backgrounds and
  capture conditions. Do not present these metrics as field-photo accuracy or
  as a guarantee on farmer-uploaded images.
- **Model:** `models/disease/disease_mobilenetv2.keras`
- **Metadata and class mapping:** `models/disease/disease_metadata.json`,
  `models/disease/class_names.json`
- **Evidence:** `reports/disease/evaluation_metrics.json`,
  `reports/disease/per_class_metrics.csv`,
  `reports/disease/confusion_matrix.png`,
  `reports/disease/test_predictions.csv`,
  `reports/disease/split_manifest.csv`,
  `reports/disease/training_history.csv`
- The failed first checkpoint attempt is preserved as
  `models/disease/incomplete_checkpoint_from_failed_run.keras`; it was not used
  for final model selection or evaluation.

## Yield regression

- **Source:** FAOSTAT Production: Crops and livestock products, normalized
  public bulk dataset:
  [download](https://bulks-faostat.fao.org/production/Production_Crops_Livestock_E_All_Data_(Normalized).zip).
- **License:** CC BY 4.0, subject to FAOSTAT Statistical Database Terms of Use
  and third-party exceptions.
- **Records:** scanned 4,209,110 source rows; selected 839,606 `Element=Yield`
  observations. Retained 822,845 area-based `kg/ha` records. Excluded 16,761
  `No/An` observations (counts, not area-based yield). Years 1961–2024; 244
  FAOSTAT countries/regions and 169 crops.
- **Inputs:** FAOSTAT `Area` (country or aggregate region), `Item` (crop), and
  `Year`. **Target:** FAOSTAT `Yield`, kg/hectare. Production, area, soil,
  rainfall, and temperature are not model inputs.
- **Split:** temporal holdout: train 1961–2011 (631,640 rows), test 2012–2024
  (191,205 rows). Categorical one-hot encoding and numeric scaling are fitted
  on training rows only. Prediction UI allows years 2012–2016 as a near-term
  supported range; this is a country/region historical estimate, not a
  field-specific or weather-conditioned forecast.
- **Measured test results:**

| Model | MAE (kg/ha) | RMSE (kg/ha) | R² |
|---|---:|---:|---:|
| LinearRegression baseline | 7,499.02 | 20,198.13 | 0.19974 |
| RandomForestRegressor | 7,202.85 | 13,220.11 | 0.65717 |

- **Model pipeline:** `models/yield/faostat_random_forest_yield.joblib`
- **Input schema and provenance:** `models/yield/yield_metadata.json`
- **Evidence:** `reports/yield/evaluation_metrics.json`,
  `reports/yield/test_predictions.csv`,
  `reports/yield/actual_vs_predicted.png`

## Integration and checks

- FastAPI loads only models whose metadata status, model path, output/class
  mapping, and artifact SHA-256 verify. Legacy `model.h5` and `yield_model.pkl`
  files remain preserved under `models/unverified_legacy/` and are not loaded.
- React forms use FastAPI for real predictions. The dashboard displays model
  identifiers, input/result details, yield units, and inference duration.
  Disease softmax is labeled a model score, not test accuracy; no treatment is
  prescribed.
- Missing model artifacts return HTTP 503 and **“Model not trained”**.
  Invalid/missing request inputs are rejected; market lookup returns
  **“Live market data unavailable”** and no fabricated price or demand.
- Offline API verification passed with non-loopback socket connections blocked.
  Disease and yield inference use local model artifacts and make no cloud or
  database requests.
- API checks passed: health, yield options, valid disease and yield inference,
  corrupt image, missing disease file, missing yield inputs, unsupported
  country, out-of-range year, unavailable model handling, and market
  unavailable handling.
- The React-to-FastAPI browser workflow was exercised with both models. A
  held-out pepper image produced the correct PlantVillage class. A sample query
  for India/Wheat/2012 returned 5,949.99 kg/hectare. These are demo examples,
  not additional evaluation metrics.
- Backend and frontend start successfully at `http://localhost:8000` and
  `http://localhost:5173`. Frontend production build, Python compilation, and
  `pip check` passed.
- Demo screenshots: `reports/screenshots/disease_prediction.png`,
  `reports/screenshots/yield_prediction.png`,
  `reports/screenshots/market_unavailable.png`,
  `reports/screenshots/invalid_image_error.png`.

## Verified environment

Hardware: Intel Core i5-3470, 4 cores/4 threads, approximately 8.5 GB RAM,
Intel HD integrated graphics (no TensorFlow GPU); approximately 143 GiB free on
D: before training. Training and inference were performed on CPU.

Active isolated Python environment: `.venv`, Python 3.13.7. Directly verified
installed versions:

| Package | Version |
|---|---:|
| tensorflow-cpu | 2.20.0 |
| Keras | 3.15.1 |
| scikit-learn | 1.9.1 |
| NumPy | 2.5.3 |
| pandas | 3.0.6 |
| SciPy | 1.18.1 |
| Pillow | 12.3.0 |
| matplotlib | 3.11.2 |
| FastAPI | 0.142.2 |
| Uvicorn | 0.54.0 |
| joblib | 1.6.0 |
| Supabase Python client | 2.32.0 |
| Node.js | 20.13.1 |
| npm | 10.5.2 |
| React / React DOM | 19.3.0 |
| Vite | 5.4.21 |

`pip check` reported no broken requirements.

## Limitations and remaining work

- No independent field-photo dataset was evaluated. Disease outputs should be
  treated as supported PlantVillage labels, not diagnoses.
- Yield performance is aggregate historical performance and varies by crop,
  region, and time. It cannot use unprovided weather/soil/farm details.
- No authorized market data API key/provider is configured; market price,
  source, update time, and demand are unavailable.
- Existing Supabase configuration is retained but inference does not depend on
  it. Supabase environment variables are present, but database connectivity
  was not tested and the prediction routes do not use the database. Market API
  key configuration is empty. Model inference is local and offline-capable.
- The disease retry log is `reports/disease_training_retry.log`; the failed
  checkpoint log is `reports/disease_training.log`.
- The actual evaluation charts, raw metrics, and source hashes are saved in the
  paths above for inspection and reproducibility.
