# Yield input-year update — 21 October 2026

The interface and API now accept 2012 through the current UTC calendar year plus five (2031 in 2026). This is an input policy, not a forecasting validation horizon. The maximum advances annually; the dataset and trained model do not update automatically.

The original saved dataset covers 1961–2024, training covers 1961–2011, and saved temporal holdout evaluation covers 2012–2024. The original recommended range 2012–2016 remains unchanged in training metadata. A separate accepted_prediction_year_range is now served to the interface. Estimates after 2024 carry the label “Experimental estimate — future accuracy not validated”. Historical results also display the training cutoff and limitations.

No retraining, data download or model conversion was performed. All files under models/ are byte-identical to the supplied archive. Existing aggregate metrics do not validate 2026 or later. Random Forest trees do not extrapolate numerical year trends beyond training thresholds. India / Maize (corn) returned 5949.99 kg/hectare for 2012, 2016, 2024, 2026, 2027 and 2031. Do not present these as independently validated annual forecasts.

## Verification

See YEAR_UPDATE_TESTS.log. Actual loaded-artifact API checks passed for historical/experimental labels, 2026/2027/2031 acceptance, lower/upper rejection, unsupported-country rejection, helper/API consistency, readiness, static dashboard HTML, sample disease inference and invalid-image handling. Frontend npm ci and production build passed. A full interactive browser check of this update has not been performed. Full future forecast evaluation has not been performed.

To repeat: install backend/requirements-deploy.txt plus httpx in an isolated environment, build frontend, copy frontend/dist to backend/static, then run check_year_update.py and check_deployment.py from project root.

## Deploy from the existing GitHub repository

Replace the existing repository-root AgriVision_Render_Free.zip with this updated archive, keeping that exact filename. Keep the existing root bootstrap Dockerfile; it already extracts that filename. Commit the replacement. If automatic deployment is enabled, Render rebuilds. Otherwise use Manual Deploy → Deploy latest commit. No new service or paid plan is required.

After deployment, open /api/yield/options and confirm accepted_prediction_year_range includes 2026. Refresh the dashboard and submit India / Maize (corn) / 2026. The result must show the experimental warning. The live site is unchanged until the updated archive is committed and deployed.
