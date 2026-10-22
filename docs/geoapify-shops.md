# Real mapped agricultural-shop search

The existing registered-shop marketplace API is retained. A separate `/api/shops/nearby` endpoint queries Geoapify Places API using its documented `commercial.agrarian` category. It does not return generic supermarkets as agricultural supply shops.

## Render setup

1. In the Geoapify AgriVision project, copy the API key privately.
2. Render → Agrivision → Environment → Add variable: `GEOAPIFY_API_KEY` = the actual Geoapify key. Do not use Render Generate for this provider key. Do not put it in GitHub, chat or a `VITE_` variable.
3. Save and deploy the latest commit. `/api/health` should then report `shop_provider_configured: true`.
4. Open Products & Shops → Nearby agricultural supply shops. Search `Tiruppur, Tamil Nadu` or allow location access.
5. If results are empty, map coverage may be incomplete. Use the existing external map search as a fallback. An empty list must not be filled with invented shops.

Browser origin restrictions for a client-side key do not automatically apply to backend requests. If restricting the key, configure restrictions compatible with requests from your backend service; a key rejected by Geoapify yields a safe HTTP 503. API keys are never returned in responses or included in error logs. Obtain/revoke keys in your own Geoapify project.

## API

- `GET /api/shops/nearby?town=Tiruppur%2C%20Tamil%20Nadu`
- `GET /api/shops/nearby?latitude=11.1085&longitude=77.3411&radius_km=25`

Queries return up to 20 mapped shops within 1–50 km. Town search uses Geoapify forward geocoding restricted to India; town results refer to the geocoded place center. Location search uses user-provided coordinates. Distances are straight-line distances, not driving distances. Returned names, addresses, coordinates and optional contact/website/opening hours are provider data and not independently verified by AgriVision. Unsafe website schemes are suppressed.

No names, stock, product prices, offers or discounts are fabricated. This provider supplies place listings, not a shopping catalog or crop-sale marketplace. Existing AGMARKNET prices still need their own working `DATA_GOV_IN_API_KEY`; adding a Geoapify key does not configure market prices.

## Usage and privacy

The backend caches successful searches in memory for five minutes (up to 256 searches). Provider calls are serialized and spaced at least 0.3 seconds apart, with a conservative 2,000 upstream-request daily cap per process. A new uncached town search uses two upstream requests. These local limits reset on restart and cannot measure other applications sharing the same key; monitor the actual Geoapify quota dashboard. Busy requests return HTTP 429 rather than queueing indefinitely. Failed requests never silently become empty successful responses.

Town/coordinates are sent to Geoapify only after an explicit user search. No user position is saved to the marketplace database. The UI displays Geoapify/OpenStreetMap attribution. The required attribution must remain visible.

## Testing

Eight provider test methods cover key absence, request construction, real-data field preservation using clearly marked provider fixtures, cache behavior, town geocoding, category/radius filtering, invalid coordinates, unsafe URLs, upstream authentication/quota errors, malformed JSON, response size limits, transport failure and the local request budget. Together with prior tests, 34 test methods pass. Vite production build passes.

No live provider lookup was tested because the private Geoapify key has not been installed in the backend. After configuring it, test an actual town/location query on the deployed version and inspect returned data and source. Do not treat a mocked-provider test as live coverage verification.

Sources:
- https://apidocs.geoapify.com/docs/places/
- https://apidocs.geoapify.com/docs/geocoding/forward-geocoding/
- https://www.geoapify.com/pricing/

## Interface update

The unavailable data.gov.in price card has been removed from Products & Shops. The header now reports Geoapify shop-provider configuration and the Render blueprint requests `GEOAPIFY_API_KEY` instead of requiring a data.gov.in key. Geoapify supplies mapped places, not crop prices or discounts. The optional legacy backend price endpoint remains for compatibility, but the dashboard no longer requests it. Existing Render secrets are not modified by editing the blueprint; preserve the already configured Geoapify key.
