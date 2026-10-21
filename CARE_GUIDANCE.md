# Care guidance and shop discovery

Added a disease-result care panel with crop-specific extension guide links, basic monitoring and selected cultural-care advice, plus optional town/district shop search. Healthy categories receive monitoring advice without a disease-treatment claim. Unsupported/failure results do not display the panel.

This is static, general guidance, not a clinical plant diagnosis, guaranteed cure, pesticide prescription, inventory feed or live price provider. The shop link is Google Maps search, not a verified seller or product catalogue. No chemical brands, doses or stock/price claims are generated. Specific chemical selection requires confirmation of diagnosis, local registration and current label instructions with an agricultural adviser. No location permission or automatic location request is used.

Sources reviewed 21 October 2026: UC IPM crop guides for tomato, potato and peppers, their bacterial spot/early blight/late blight pages, and TNAU tomato leaf curl, mosaic and Septoria pages. Source URLs are in frontend/src/components/DiseaseCare.jsx. California guides do not establish Indian product approval; TNAU recommendations may be older. External links require internet access; embedded text remains available when the frontend runs locally.

The model files and year-update functionality are preserved. The separate live market-price module remains unavailable. Frontend production build verified; current interactive browser layout and real shop stock/licences not verified.
