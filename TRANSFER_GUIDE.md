# AgriVision transfer and setup guide

This guide applies to the contents of `AgriVision_Transfer.zip`. Use it in
preference to older setup notes and feature descriptions in the source tree;
some describe planned functionality rather than the verified local demo.
`HOD_DEMO.md` lists the demonstrated features and limitations. No model
retraining or cloud credentials are required for local inference.

## Target computer and versions

- **Target:** Dell Inspiron N5010, Intel Core i5 M480, 8 GB RAM, Windows 10
  64-bit, CPU only.
- **Versions verified on the college PC:** Python 3.13.7, Node.js 20.13.1,
  npm 10.5.2.
- **Python dependencies:** exact versions pinned in
  `backend\requirements.txt`. The disease model uses TensorFlow CPU; the yield
  model uses scikit-learn/joblib. There is no separate Python lockfile.
- **Frontend dependencies:** pinned by `frontend\package-lock.json`; use
  `npm ci`, not `npm install`.

The laptop has a much older CPU than the college PC. TensorFlow wheel
compatibility and inference speed on the i5 M480 have **not** been verified.
The CPU may lack instruction sets used by current TensorFlow builds, and 8 GB
of RAM may cause paging. If TensorFlow reports an illegal-instruction error,
stop rather than attempting to retrain or install random alternate packages.
Home-laptop startup, inference, available memory, and performance must be
tested there.

## Extract and install

Install 64-bit Python 3.13.7 (with the Python launcher) and Node.js 20.13.1
first. Open PowerShell and run:

```powershell
$destination = Join-Path $HOME 'AgriVision_Transfer'
Expand-Archive -LiteralPath (Join-Path $HOME 'Downloads\AgriVision_Transfer.zip') -DestinationPath $destination
Set-Location $destination

Copy-Item .env.example .env
py -3.13 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r .\backend\requirements.txt

Set-Location .\frontend
npm ci
```

If Python is installed under a different minor version, do not silently change
the pinned ML stack: verify all packages install and both models load before
the demonstration.

## Start the application

Keep two PowerShell windows open.

**Window 1 — backend:**

```powershell
Set-Location (Join-Path $HOME 'AgriVision_Transfer\backend')
& ..\.venv\Scripts\python.exe -m uvicorn app.main:app --host localhost --port 8000
```

**Window 2 — frontend:**

```powershell
Set-Location (Join-Path $HOME 'AgriVision_Transfer\frontend')
npm run dev -- --host localhost --port 5173
```

Open `http://localhost:5173`. Check `http://localhost:8000/api/health` and
confirm both `disease_model_available` and `yield_model_available` are
`true`. Interactive API documentation is at `http://localhost:8000/docs`.
Keep the host set to `localhost`; do not expose the development server to a
public network.

## Models, preprocessing, and configuration

The backend resolves model paths relative to the extracted project root; the
`.env` paths do not override this loader:

- Disease model: `models\disease\disease_mobilenetv2.keras`
- Disease class mapping: `models\disease\class_names.json`
- Disease preprocessing and training metadata: `models\disease\disease_metadata.json`
- Yield model pipeline: `models\yield\faostat_random_forest_yield.joblib`
- Yield input schema and provenance: `models\yield\yield_metadata.json`

The disease API accepts JPG/PNG images, decodes RGB, resizes to 160x160, and
passes RGB values in the 0..255 range to the model, which performs its saved
rescaling. Yield inference accepts a FAOSTAT country/region, crop, and year;
the pipeline contains its fitted preprocessing. At startup, the backend
checks each model file's SHA-256 against its metadata and reports missing or
invalid artifacts through the health endpoint.

`.env.example` contains no credentials; optional integration keys are blank.
Local disease and yield inference does not require Supabase, market-data,
Gemini, or Groq credentials. Only fill those keys when separately configuring
an authorized service; do not put private keys in a transfer archive.

## Included and excluded

The archive includes frontend/backend source, ML training and evaluation
scripts, exact dependency files, the two hash-verified inference models,
metadata/class mappings, evaluation reports, prediction CSVs, plots, existing
demo screenshots, and three CC0 PlantVillage images for smoke testing. Raw
datasets, extracted dataset collections, legacy/unverified models, credentials,
virtual environments, `node_modules`, build output, caches, and Git history
are excluded. Raw training data is not required for inference; training
scripts are included but are not part of setup.

The UI, local prediction endpoints, and both model artifacts worked on the
college PC. Startup and inference on the Dell laptop remain to be tested;
live market data and database-backed functionality are not verified features
of this local transfer.
