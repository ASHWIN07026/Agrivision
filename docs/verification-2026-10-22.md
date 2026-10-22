# AgriVision verification — 22 October 2026

## Changes

Docker now builds the tracked frontend/backend/models, rather than extracting the stale `AgriVision_Render_Free.zip`. No original disease/yield weights or design styles changed.

Disease uploads pass format, byte/pixel limits, minimum dimensions and an independent offline CLIP vision/text similarity gate before invoking the disease classifier. Missing/corrupt validator assets fail closed with HTTP 503. Negative decisions return HTTP 422 without disease/confidence fields. Crop mismatch, low confidence and non-finite model output are rejected. Health includes validator availability and Render's `RENDER_GIT_COMMIT`; readiness includes all three models.

The new validator is Xenova's quantized ONNX conversion of OpenAI CLIP ViT-B/32. It runs locally without an API key or uploading user photos. Model URL is pinned to a Hugging Face commit and checked by SHA-256. Docker downloads the 85 MB vision artifact at build time; runtime needs no model network access. Text embeddings and their preparation script are tracked. Source: https://huggingface.co/Xenova/clip-vit-base-patch32 (upstream: https://huggingface.co/openai/clip-vit-base-patch32; MIT license). The upstream model's limitations still apply.

AGMARKNET lookup retains official records only, requests descending observation dates, validates dates and finite ordered prices, and displays mandi/district/state/date/source and INR/quintal units. Failed new requests clear previous prices. Provider authentication, rate limits, malformed replies and missing keys never create prices. The endpoint returns up to 10 records from the provider's first 100 matches; inspect displayed dates rather than assuming nationwide completeness or live trading prices.

## Secure market setup

1. Sign into https://www.data.gov.in/ and obtain your own API key for the Current Daily Price of Various Commodities from Various Markets (Mandi) resource, ID `9ef84268-d588-465a-a308-a864a43d0070`.
2. In Render → AgriVision → Environment, add `DATA_GOV_IN_API_KEY` as a secret environment variable and save/redeploy. `render.yaml` declares it with `sync: false`.
3. Never use a `VITE_` variable for this key, commit `.env`, paste it into source, or log the upstream request URL. For local use, export it in the backend process environment; the app does not automatically load `.env`.
4. Verify `/api/health` reports `market_api_configured: true`, then request `/api/market/price?crop=Tomato&state=Tamil%20Nadu`. A configured key does not by itself prove provider connectivity or data freshness.

No real key was available in this session. Successful market responses were tested with clearly mocked provider fixtures, not claimed as live market observations.

## Authentication findings

No Firebase SDK, Firebase config, signup/login/logout implementation or protected pages exists in the current `main` source or deployed ZIP. `docs/authentication.md` explicitly says authentication was removed. Existing optional Supabase files were left unchanged. Unused translated authentication strings are not a working authentication feature. Firebase account-flow tests are therefore blocked pending the intended Firebase implementation/project configuration; the dashboard remains publicly accessible as it was before.

## Reproduction

```sh
python -m pip install -r backend/requirements-deploy.txt httpx
python scripts/download_leaf_validator.py
python scripts/download_validation_fixtures.py
OPENBLAS_NUM_THREADS=1 AGRIVISION_NEGATIVE_FIXTURES=/tmp/agrivision-validation PYTHONPATH=backend python -m unittest discover -s backend/tests -v
npm ci --prefix frontend
npm run build --prefix frontend
```

17 unittest methods passed, including actual inference for tomato healthy, potato early blight and bell pepper bacterial spot; actual independent person/cat/bus rejection before disease inference; corrupt/empty/oversized/flat images; validator outage; crop mismatch; readiness; real yield inference and invalid inputs; and mocked AGMARKNET success/error/malformed data. Production Vite build passed. Deployment requirements installed successfully in Python 3.12. Docker is unavailable in the test host, so a full image build was not executed locally.

## Limits and deployment checks

The three positive and three negative photos are regression examples, not a representative agricultural field-validation dataset. CLIP is a general zero-shot model: it does not establish botanical species, detect every mixed-content scene or guarantee rejection of every unrelated image. Broader held-out evaluation is required before claiming rejection accuracy. The original disease model remains a PlantVillage classifier with its original domain limits.

The test process peaked near 477 MiB, including test payloads. Watch Render free-instance memory during deployment and larger uploads; do not increase worker count without profiling. The build requires public Hugging Face download access and fails if its checksum differs. Existing yield forecasts remain experimental beyond the training period.

After pushing, compare `/api/health` → `revision` to the new GitHub commit, verify `/api/ready`, repeat positive/negative disease uploads, yield inference and market configuration checks on the live origin. If Render auto-deploy is off or the build fails, service dashboard access/logs are needed; GitHub push alone is not deployment verification.
