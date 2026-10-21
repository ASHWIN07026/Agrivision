# Verified source datasets

Downloaded raw archives and extracted images are ignored by Git. Provenance
metadata and reproducible preparation/training scripts remain in the repository.

## PlantVillage leaf images

- Source: [Mendeley Data, DOI 10.17632/tywbtsjrjv.1](https://data.mendeley.com/datasets/tywbtsjrjv/1); downloaded through the public URL used by [TensorFlow Datasets](https://www.tensorflow.org/datasets/catalog/plant_village).
- License shown on the Mendeley record: CC0 1.0.
- Download: `source_archives/plant_village_without_augmentation.zip` (868,032,562 bytes).
- The unaugmented archive contains 39 label folders and 55,448 images; this includes the `Background_without_leaves` folder. The model uses only the 15 Tomato, Potato, and Pepper disease/healthy categories listed in `plantvillage_source.json`; it does not train on the background class or the augmented images.
- Per-class source counts, archive checksum, extraction details, deduplication, and split counts are recorded in `plantvillage_source.json`, `models/disease/disease_metadata.json`, and `reports/disease/`.

Prepare the crop subset with:

```powershell
.\.venv\Scripts\python.exe ml\disease\prepare_plantvillage_subset.py
```

## FAOSTAT crop yields

- Source: [FAOSTAT Production: Crops and livestock products](https://www.fao.org/faostat/en/#data/QCL), normalized public bulk file: [download](https://bulks-faostat.fao.org/production/Production_Crops_Livestock_E_All_Data_(Normalized).zip).
- Download: `source_archives/faostat_crops_livestock_normalized.zip` (33,921,825 bytes).
- License: CC BY 4.0 under FAOSTAT Statistical Database Terms of Use, subject to any third-party exceptions and required attribution.
- CSV member and columns used: `Area` (country/region), `Item` (agricultural product), `Element` (filtered to `Yield`), `Year`, `Unit`, and `Value`.
- Only area-based yield observations are kept and converted to kg/hectare. `No/An` rows are excluded because they are not area-based yield units. No production or area feature is used to predict yield.
- The current source contains records for 244 areas and 169 crop items from 1961–2024. Exact filtered row counts, units, archive checksum, and model split details are in `models/yield/yield_metadata.json`.
