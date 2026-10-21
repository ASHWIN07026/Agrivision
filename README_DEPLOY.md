# AgriVision: low-memory deployment candidate

Status: local build and API checks pass. NOT publicly deployed. Docker build is unverified here.

This variant serves the existing React dashboard and FastAPI on one origin. It runs the trained disease network as a float32 LiteRT artifact, without full TensorFlow at runtime. No retraining or quantization was performed. Original Keras model, class mapping, metadata and yield pipeline are preserved.

## Verified here

- Frontend production build passes (inherited unchanged from tested single-origin package).
- Both models load, API readiness returns 200, static dashboard HTML serves.
- Yield India / Maize (corn) / 2016: 5949.99 kg/ha.
- Three provided disease samples give the same class labels as the Keras reference.
- On identical preprocessed tensors, LiteRT versus Keras maximum score error was below 0.000002 on these samples.
- NumPy antialias bilinear resizing differs from TensorFlow by less than 0.001 on those decoded images.
- Full JPEG pipelines use different decoders. Maximum sample score difference was 0.05391 (about 5.39 percentage points), even though all three labels matched.
- Measured peak resident memory of local API integration checks: 238.8 MiB, versus 769.8 MiB for full TensorFlow. Additional testing with a maximum-size 4MP upload peaked at 319.6 MiB. This is not a guarantee of hosted memory under arbitrary traffic.
- Invalid images and unsupported 2026 yield inputs are rejected; live market remains unavailable.

The original 83.45% accuracy describes the original Keras/PlantVillage evaluation, NOT a fresh evaluation of this LiteRT deployment. Full 731-image LiteRT evaluation and field-photo validation remain outstanding. See conversion_validation.json and lite-test.log.

## Render

Use a GitHub repository with the package CONTENTS at its root, not a ZIP stored inside the repository. Dockerfile, backend, frontend and models must all be present. Select a Docker Web Service with Free instance type; leave Root Directory blank. Set health check /api/ready and use one worker. PORT is provided by Render; the command binds 0.0.0.0:$PORT.

Do not upgrade or add payment details to satisfy this package. Account eligibility, resource availability and current free limits must be checked in the dashboard. Free instances may sleep and cold-start slowly. Successful local tests do not prove a successful deployment.

No API credentials or database connection are required for the existing disease and yield inference. Do not upload real .env or api.txt.

## Host-independent local checks

```
docker build -t agrivision-lite .
docker run --rm -p 7860:7860 agrivision-lite
```

Docker build was not executed here. To rerun Python TestClient checks, install backend/requirements-deploy.txt plus httpx in an isolated Python 3.12 environment and run check_deployment.py. Build frontend and copy frontend/dist into backend/static first if not present.

## Scope and input limits

Disease: 15 classes of tomato, potato and bell pepper, JPG/PNG, max 10 MiB and 4 megapixels. Yield: country/region, crop and historical year 2012-2016 in the current API. Dataset evaluation includes 2012-2024. No validated 2026 forecasting, live market/news integration or verified database persistence.
