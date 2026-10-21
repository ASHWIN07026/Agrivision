# Corrected presentation text

Use these replacements for the old **Result** and **Conclusion** slides. These
claims reflect the measured local artifacts and tested API/dashboard.

## Result

- **Plant disease classification:** A MobileNetV2 transfer-learning model was
  trained on 3,653 sampled images from a 15-class, Tomato/Potato/Bell pepper
  PlantVillage subset. Duplicate and perceptually related images were grouped
  before the stratified train/validation/test split. On 731 held-out
  PlantVillage images, measured accuracy was **83.45%**, macro precision
  **84.48%**, macro recall **83.78%**, and macro F1 **83.47%**.
- **Yield estimation:** A RandomForestRegressor was trained using real FAOSTAT
  crop yield records with country/region, crop, and year as inputs. On a
  time-based 2012–2024 holdout it achieved **MAE 7,202.85 kg/ha**, **RMSE
  13,220.11 kg/ha**, and **R² 0.65717**. The LinearRegression baseline scored
  MAE 7,499.02 kg/ha, RMSE 20,198.13 kg/ha, and R² 0.19974.
- **Integration:** React forms call local FastAPI prediction endpoints and
  return results from the saved models. Model artifacts and class/schema
  metadata are hash-verified at load time. Missing artifacts are reported as
  “Model not trained.”
- **Market data:** No authorized live API is configured; price and demand
  lookup is explicitly unavailable rather than simulated.
- **Scope:** PlantVillage results do not establish field-photo accuracy.
  Yield outputs are historical country/region estimates; no soil or weather
  inputs are used.

## Conclusion

The AgriVision dashboard now runs a locally trained 15-class PlantVillage
MobileNetV2 classifier and a FAOSTAT-based Random Forest yield estimator
through FastAPI. Their measured results and evaluation artifacts are saved in
`RESULTS.md` and `reports/`. Disease and yield inference work without cloud
services or a database connection. The disease evaluation is limited to
PlantVillage's controlled images, and the yield model estimates historical
country/region outcomes from crop and year rather than field-specific
conditions. Live market prices remain unavailable until an authorized
provider is configured.
