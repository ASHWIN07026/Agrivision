# Manual leaf-care lookup

The Disease Detection page now includes a separate Leaf care lookup with exactly seven requested leaf names and two care topics: Early Blight and Powdery Mildew. It contains 14 explicit mappings to four reusable management protocols in `frontend/src/data/leafCareLookup.json`.

Each guide includes diagnosis/preparation, organic/nonchemical options, chemical alternatives, preparation/application methods, monitoring and harvest precautions, and source links. The six tomato varieties share general tomato management guidance; no cultivar-specific dose or efficacy is asserted.

Tulsi is not treated as a tomato. The Early Blight pairing requires diagnostic confirmation, and both Tulsi guides require crop-specific local registration before any pesticide use. Sweet-basil references do not establish approval or efficacy on Holy Basil. No universal dilution, guaranteed cure or fixed harvest interval is supplied. Damaged tissue cannot be restored by a fungicide. Products, organic approvals, rates, permitted combinations, temperature limits and repeat/harvest/re-entry intervals depend on the actual current label.

The application steps explain measuring a label-specified dilution for the chosen water volume, label mixing order, sprayer coverage, protective equipment, environmental conditions, avoiding unauthorised mixtures, equipment cleanup and treatment records. Oil/sulfur incompatibility and heat restrictions are explicit in the tomato Powdery Mildew guide. Sulfur is presented mainly as protection against new infections, not a repair for already damaged foliage.

This is a manual reference feature, not a newly trained image classifier. Original disease/yield model weights, class mapping and prediction routes remain unchanged. Neither Tulsi nor Powdery Mildew nor cultivar-level identity is added to the model's supported predictions. `image_prediction_supported: false` identifies every reference mapping as outside model-specific validation, even though the existing model supports tomato Early Blight generally.

Validation: the frontend production build passed; data checks confirmed exactly 14 unique combinations, resolvable protocols/source references and manual-only scope. No disease-model retraining or cultivar/Tulsi efficacy testing was performed. Care steps currently use English, while the existing interface's language selector remains available for its already translated labels.

## Automatic results and phone camera

The disease form defaults to `crop=auto`. The existing classifier's class determines tomato, potato or bell pepper after the same independent image validation and confidence checks. Explicit crop selections still reject mismatched results. This does not identify tomato cultivars, Tulsi or Powdery Mildew, and does not add training classes.

A successful prediction opens its existing care guidance automatically. Tomato Early Blight also displays the shared sourced, five-stage care protocol used by the manual lookup. Rejected images display neither a prediction nor treatment guidance.

“Take photo” uses the browser's native rear-camera file capture hint; browser support varies and desktops may show a file picker. Captured JPG/PNG photos are resized to a maximum edge of 1600 pixels when needed before upload. Gallery uploads retain their original handling. Capture cancellation leaves the previous selection unchanged. Physical Android camera behavior must be checked on a device after deployment.

Checks: `node --test frontend/tests/cameraPhoto.test.js`, `npm run build --prefix frontend`, and the backend unittest suite, including automatic crop classification, explicit crop mismatch, invalid images and negative photo rejection.
