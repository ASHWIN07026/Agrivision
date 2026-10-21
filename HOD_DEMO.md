# AgriVision HOD demonstration

## Start and verify

Follow `TRANSFER_GUIDE.md` to install dependencies and start the backend and
frontend in separate PowerShell windows. Open `http://localhost:5173` and
`http://localhost:8000/api/health`; verify the disease and yield models are
available before presenting.

## Disease prediction

1. Open **Disease Detection** and upload one of the JPG test images in
   `samples\` (or a suitable JPG/PNG leaf image).
2. Show the predicted PlantVillage label and its score. Explain that this is a
   model softmax score, **not** the model's test accuracy or a treatment
   recommendation.
3. The verified classifier covers 15 Tomato, Potato, and Bell pepper disease
   or healthy categories. It was evaluated on controlled PlantVillage images;
   accuracy on field photographs has not been established.

## Yield prediction

1. Open **Yield Estimation** and select a country/region, crop, and year from
   the UI's supported range of **2012–2016**.
2. Submit the form and show the estimated yield in **kg/hectare**.
3. State clearly that the only inputs are **country/region, crop, and year**.
   The model does not take soil, rainfall, temperature, or farm-level location
   as inputs.

## Measured evaluation and data

**Disease classifier**

- Source: PlantVillage unaugmented archive (Mendeley Data,
  DOI `10.17632/tywbtsjrjv.1`), shown as CC0 1.0.
- Scope: 22,787 source images across the selected 15 Tomato, Potato, and
  Bell pepper classes; 3,653 images sampled for the run.
- Split: duplicate/perceptual-image groups were kept together; train 2,337,
  validation 585, test 731.
- Held-out test results (731 images): accuracy **83.45%**, macro precision
  **84.48%**, macro recall **83.78%**, macro F1 **83.47%**.
- Measured on the college CPU: warm API model-predict median **92.26 ms/image**
  (7 requests, first excluded); cold first request **1,382.54 ms**. These
  exclude image decoding/resizing. Batched test-evaluation average was
  **28.56 ms/image** and is a different measurement. Hardware and load affect
  timings.

**Yield estimator**

- Source: FAOSTAT Production: Crops and livestock products, normalized public
  dataset; CC BY 4.0 subject to FAOSTAT terms and third-party exceptions.
- Data: 822,845 area-based `kg/ha` yield records, 244 countries/regions and
  169 crops, 1961–2024. The temporal split trained on 1961–2011 and tested on
  2012–2024 (191,205 held-out records).
- Random Forest test results: MAE **7,202.85 kg/ha**, RMSE
  **13,220.11 kg/ha**, R² **0.65717**. Linear Regression baseline: MAE
  7,499.02 kg/ha, RMSE 20,198.13 kg/ha, R² 0.19974.
- These are historical country/region estimates, not farm-specific forecasts.
  The UI's 2012–2016 range is narrower than the evaluation holdout.

Detailed metrics, class-wise results, predictions, split evidence, and plots
are in `RESULTS.md` and `reports\`.

## Unavailable or unverified

- **Live market prices, trends, and demand:** unavailable. No verified,
  authorized market provider is configured; do not present simulated values.
- **Field-photo disease accuracy:** unverified. PlantVillage test performance
  does not establish accuracy on field/farmer photographs.
- **Database functionality:** Supabase/database-backed features such as
  persistence, accounts, or prediction history have not been validated for
  this transfer. The demonstrated local model predictions do not require a
  database.
- **Target laptop:** setup and inference on the Dell Inspiron N5010 have not
  yet been tested. Use the compatibility notes in `TRANSFER_GUIDE.md`.

Existing UI evidence is under `reports\screenshots\`: disease prediction,
yield prediction, market unavailable, and invalid-image error.
