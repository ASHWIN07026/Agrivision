# AgriVision agriculture marketplace API

This is an AgriVision-owned API for seller/buyer submissions and registered shops. It is independent of `DATA_GOV_IN_API_KEY`; no external market-data key is required. It does not generate third-party prices, inventory, discounts, shops or buyers.

## Included features

- Agriculture categories: produce, seeds, fertilizers, crop protection, tools, machinery, irrigation and animal feed.
- Sell listings (products a buyer can enquire about) and buy listings (buyer requirements a seller can respond to).
- INR prices and quantities with explicit units. These are seller asking prices or buyer budgets, not official mandi prices.
- Time-limited offers, calculated discount percentages, expired-offer exclusion and listing withdrawal.
- Registered agriculture shops, category filters, latitude/longitude radius search and distance sorting.
- A new frontend marketplace panel in the existing supplies section. It includes listings, active offers, contact links, location permission and directions. Existing online-shop search and official price lookup remain separate.
- Public read access and administrator-only publishing. No real test listings are seeded. Phone numbers require explicit public-contact consent.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/marketplace/options` | Categories and service scope |
| GET | `/api/marketplace/listings` | Filter listings by intent, category, district, state, query or shop; pagination and active offers |
| GET | `/api/marketplace/offers` | Active discounted sell listings |
| GET | `/api/marketplace/shops/nearby?latitude=11.1&longitude=77.3&radius_km=25` | Nearby registered shops; coordinates here are illustrative |
| POST | `/api/marketplace/shops` | Administrator registers a real shop |
| POST | `/api/marketplace/listings` | Administrator publishes a real seller/buyer submission |
| DELETE | `/api/marketplace/listings/{id}` | Administrator withdraws a listing |

Interactive API documentation is at `/docs` after starting/deploying the backend. The new endpoints are not available on the live Render site until the code is deployed.

## Local startup

For the full project, install `backend/requirements-deploy.txt` and the validator as described in the verification report. For just this marketplace API, the standalone ZIP uses only FastAPI, Pydantic and Uvicorn.

Choose a private database path, set `MARKETPLACE_DB_PATH`, and generate a server-only administrator key with Python's `secrets.token_urlsafe(32)`. Set the resulting value as `MARKETPLACE_ADMIN_KEY` in the backend environment. Do not commit it, put it in a `VITE_` setting, or include it in public frontend requests. There is no built-in administrator password. If the key is absent or shorter than 32 characters, publishing is disabled.

Start the full backend from `backend/`:

```sh
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In `/docs`, a publishing request takes an `Authorization` header containing `Bearer YOUR_PRIVATE_ADMINISTRATOR_KEY`. Public GET endpoints need no key. Publish only real submissions for which the contact person has consented; use `public_contact_consent: true` for that consent. Offer prices require a lower price plus a future timezone-aware expiry datetime. Money accepts no more than two decimal places.

## Deployment and persistence

SQLite has no third-party API charge and works for a small single-instance prototype. It is NOT a shared multi-instance database. Queries currently scan the small stored listing/shop tables in application memory; migrate to indexed spatial/relational queries before scaling.

Render's free local filesystem is ephemeral: listings can disappear on restart/redeploy. Production publishing on Render is disabled unless `MARKETPLACE_DB_PATH` is explicitly configured. That path must actually point to a persistent mounted disk (for example `/var/data/marketplace.sqlite3`) or replace the storage layer with an appropriate hosted database. Merely setting an ordinary temporary path does not make it durable. Persistent Render storage may require a paid plan. No disk, hosting upgrade or paid service was provisioned by this change.

The administrator key grants publishing access, so retain it server-side and use HTTPS remotely. This is an administrator-managed marketplace, not a self-service seller authentication system. Existing Firebase/account features were not added or replaced. Public personal-contact data must be submitted with consent.

## Explicit limits

- Registered shops only; this is not an exhaustive nearby-shop directory. Empty results do not mean no shops exist.
- No automatic live offers or stock from BigHaat, AgriBegri or other stores; these require authorised feeds or seller submissions.
- No checkout, payment, escrow, shipping or order fulfilment. Buyers and sellers contact each other for enquiries. Transactional commerce requires additional implementation and provider setup.
- Categories constrain agriculture scope, while the administrator remains responsible for reviewing submitted descriptions and products.
- Offer and listing expiry use UTC; the frontend displays offer times in the viewer's local timezone. Refresh searches for current availability.
- No claim that seller-entered prices or discounts are independently verified.

## Validation

Nine marketplace test methods cover unauthenticated access, missing key/storage configuration, real database persistence, filters, pagination, offer calculations and expiry, invalid prices/categories/contact consent, listing expiry/withdrawal, shop radius/category/coordinate validation and HTTPS website validation. They use isolated temporary databases and fictional test fixtures, never production data.

Together with existing tests, 26 test methods passed. The production frontend build passed. No live deployment is claimed; the previously confirmed GitHub write-access blocker must be resolved before the commit can be pushed and Render deployment verified.
