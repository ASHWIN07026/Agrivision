# Manual leaf-care lookup

The Disease Detection page now includes a separate Leaf care lookup with exactly seven requested leaf names and two care topics: Early Blight and Powdery Mildew. It contains 14 explicit mappings to four reusable management protocols in `frontend/src/data/leafCareLookup.json`.

Each guide includes diagnosis/preparation, organic/nonchemical options, chemical alternatives, preparation/application methods, monitoring and harvest precautions, and source links. The six tomato varieties share general tomato management guidance; no cultivar-specific dose or efficacy is asserted.

Tulsi is not treated as a tomato. The Early Blight pairing requires diagnostic confirmation, and both Tulsi guides require crop-specific local registration before any pesticide use. Sweet-basil references do not establish approval or efficacy on Holy Basil. No universal dilution, guaranteed cure or fixed harvest interval is supplied. Damaged tissue cannot be restored by a fungicide. Products, organic approvals, rates, permitted combinations, temperature limits and repeat/harvest/re-entry intervals depend on the actual current label.

The application steps explain measuring a label-specified dilution for the chosen water volume, label mixing order, sprayer coverage, protective equipment, environmental conditions, avoiding unauthorised mixtures, equipment cleanup and treatment records. Oil/sulfur incompatibility and heat restrictions are explicit in the tomato Powdery Mildew guide. Sulfur is presented mainly as protection against new infections, not a repair for already damaged foliage.

This is a manual reference feature, not a newly trained image classifier. Original disease/yield model weights, class mapping and prediction routes remain unchanged. Neither Tulsi nor Powdery Mildew nor cultivar-level identity is added to the model's supported predictions. `image_prediction_supported: false` identifies every reference mapping as outside model-specific validation, even though the existing model supports tomato Early Blight generally.

Validation: the frontend production build passed; data checks confirmed exactly 14 unique combinations, resolvable protocols/source references and manual-only scope. No disease-model retraining or cultivar/Tulsi efficacy testing was performed. Care steps currently use English, while the existing interface's language selector remains available for its already translated labels.
