"""AgriVision-owned listings API. No third-party prices, offers or shops are fabricated."""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Decimal
import hmac
import json
import math
import os
from pathlib import Path
import sqlite3
from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

router = APIRouter(prefix='/api/marketplace', tags=['Agriculture Marketplace'])
Category = Literal['produce', 'seeds', 'fertilizers', 'crop_protection', 'tools', 'machinery', 'irrigation', 'animal_feed']
CATEGORIES = ['produce', 'seeds', 'fertilizers', 'crop_protection', 'tools', 'machinery', 'irrigation', 'animal_feed']
Money = Decimal


def utcnow():
    return datetime.now(timezone.utc)


def _future(value, field):
    if value is not None and (value.utcoffset() is None or value <= utcnow()):
        raise ValueError(f'{field} must be a future datetime with a timezone.')


class Contact(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    name: str = Field(min_length=2, max_length=100)
    phone: str = Field(pattern=r'^\+?[0-9][0-9 ()-]{6,19}$')
    public_contact_consent: Literal[True]


class ShopInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True, allow_inf_nan=False)
    name: str = Field(min_length=2, max_length=120)
    categories: list[Category] = Field(min_length=1, max_length=8)
    address: str = Field(min_length=5, max_length=300)
    district: str = Field(min_length=2, max_length=100)
    state: str = Field(min_length=2, max_length=100)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    contact: Contact
    website: HttpUrl | None = None

    @model_validator(mode='after')
    def secure_website(self):
        if self.website is not None and self.website.scheme != 'https':
            raise ValueError('Website must use HTTPS.')
        return self


class ListingInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True, allow_inf_nan=False)
    intent: Literal['buy', 'sell']
    category: Category
    title: str = Field(min_length=3, max_length=150)
    description: str = Field(min_length=5, max_length=2000)
    price_inr: Money = Field(gt=0, le=100000000, max_digits=12, decimal_places=2)
    unit: Literal['kg', 'quintal', 'tonne', 'litre', 'piece', 'packet', 'bag']
    quantity: Decimal = Field(gt=0, le=100000000, max_digits=14, decimal_places=4)
    district: str = Field(min_length=2, max_length=100)
    state: str = Field(min_length=2, max_length=100)
    contact: Contact
    shop_id: str | None = Field(default=None, max_length=36)
    offer_price_inr: Money | None = Field(default=None, gt=0, le=100000000, max_digits=12, decimal_places=2)
    offer_expires_at: datetime | None = None
    expires_at: datetime | None = None

    @model_validator(mode='after')
    def valid_offer(self):
        _future(self.expires_at, 'expires_at')
        _future(self.offer_expires_at, 'offer_expires_at')
        if (self.offer_price_inr is None) != (self.offer_expires_at is None):
            raise ValueError('An offer requires both offer_price_inr and offer_expires_at.')
        if self.offer_price_inr is not None:
            if self.intent != 'sell' or self.offer_price_inr >= self.price_inr:
                raise ValueError('Only sell listings can have an offer below the regular price.')
            if self.expires_at and self.offer_expires_at > self.expires_at:
                raise ValueError('An offer cannot outlast its listing.')
        return self


def require_admin(authorization: str | None = Header(default=None)):
    expected = os.environ.get('MARKETPLACE_ADMIN_KEY', '')
    if len(expected) < 32:
        raise HTTPException(503, 'Marketplace publishing is not configured. Set a server-only MARKETPLACE_ADMIN_KEY of at least 32 characters.')
    supplied = authorization.removeprefix('Bearer ') if authorization and authorization.startswith('Bearer ') else ''
    if not hmac.compare_digest(supplied.encode(), expected.encode()):
        raise HTTPException(401, 'Valid marketplace administrator credentials are required.', headers={'WWW-Authenticate': 'Bearer'})
    if os.environ.get('RENDER') and not os.environ.get('MARKETPLACE_DB_PATH'):
        raise HTTPException(503, 'Configure MARKETPLACE_DB_PATH on persistent storage before publishing on Render.')


@contextmanager
def database():
    path = Path(os.environ.get('MARKETPLACE_DB_PATH', str(Path(__file__).resolve().parents[2] / 'data' / 'marketplace.sqlite3')))
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=10)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute('CREATE TABLE IF NOT EXISTS shops (id TEXT PRIMARY KEY, payload TEXT NOT NULL, created_at TEXT NOT NULL)')
        connection.execute('CREATE TABLE IF NOT EXISTS listings (id TEXT PRIMARY KEY, payload TEXT NOT NULL, created_at TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1)')
        yield connection
        connection.commit()
    finally:
        connection.close()


def _shop(row):
    return {'id': row['id'], **json.loads(row['payload']), 'created_at': row['created_at'], 'source': 'shop-provided; entered by AgriVision administrator', 'verified': False}


def _listing(row):
    data = json.loads(row['payload'])
    now = utcnow()
    if not row['active'] or (data.get('expires_at') and datetime.fromisoformat(data['expires_at']) <= now):
        return None
    offer_active = bool(data.get('offer_price_inr') and datetime.fromisoformat(data['offer_expires_at']) > now)
    base = Decimal(data['price_inr'])
    effective = Decimal(data['offer_price_inr']) if offer_active else base
    return {'id': row['id'], **data, 'created_at': row['created_at'],
            'offer_active': offer_active, 'effective_price_inr': str(effective),
            'discount_percent': str(((base-effective)/base*100).quantize(Decimal('.01'))),
            'currency': 'INR', 'source': 'seller/buyer-provided; entered by AgriVision administrator',
            'price_kind': 'seller asking price' if data['intent'] == 'sell' else 'buyer budget',
            'verified': False}


def distance_km(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2-p1)/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(math.radians(lon2-lon1)/2)**2
    return 6371.0088 * 2 * math.asin(math.sqrt(min(1, max(0, a))))


@router.get('/options')
def options():
    return {'categories': CATEGORIES, 'currency': 'INR', 'publishing': 'administrator-managed',
            'data_source': 'Only actual seller, buyer and shop submissions. No automatic third-party stock or discount feed.',
            'checkout_available': False}


@router.post('/shops', status_code=201, dependencies=[Depends(require_admin)])
def create_shop(data: ShopInput):
    identifier, created = str(uuid4()), utcnow().isoformat()
    with database() as db:
        db.execute('INSERT INTO shops VALUES (?, ?, ?)', (identifier, data.model_dump_json(), created))
    return {'id': identifier, 'status': 'created'}


@router.get('/shops/nearby')
def nearby(latitude: float = Query(ge=-90, le=90), longitude: float = Query(ge=-180, le=180),
           radius_km: float = Query(default=10, gt=0, le=100, allow_inf_nan=False),
           category: Category | None = None, limit: int = Query(default=20, ge=1, le=100)):
    if not math.isfinite(latitude) or not math.isfinite(longitude):
        raise HTTPException(422, 'Coordinates must be finite.')
    with database() as db:
        rows = db.execute('SELECT * FROM shops').fetchall()
    found = []
    for row in rows:
        shop = _shop(row)
        if category and category not in shop['categories']:
            continue
        distance = distance_km(latitude, longitude, shop['latitude'], shop['longitude'])
        if distance <= radius_km:
            found.append({**shop, 'distance_km': round(distance, 2)})
    found.sort(key=lambda item: (item['distance_km'], item['id']))
    return {'status': 'ok' if found else 'not_found', 'records': found[:limit],
            'message': 'Only shops registered with AgriVision are included; an empty result does not mean no nearby shops exist.'}


@router.post('/listings', status_code=201, dependencies=[Depends(require_admin)])
def create_listing(data: ListingInput):
    identifier, created = str(uuid4()), utcnow().isoformat()
    with database() as db:
        if data.shop_id and not db.execute('SELECT id FROM shops WHERE id = ?', (data.shop_id,)).fetchone():
            raise HTTPException(422, 'shop_id does not identify a registered shop.')
        db.execute('INSERT INTO listings VALUES (?, ?, ?, 1)', (identifier, data.model_dump_json(), created))
    return {'id': identifier, 'status': 'created'}


def find_listings(intent=None, category=None, q=None, state=None, district=None, shop_id=None, offers_only=False, limit=20, offset=0):
    with database() as db:
        rows = db.execute('SELECT * FROM listings WHERE active = 1 ORDER BY created_at DESC, id').fetchall()
    result = []
    for row in rows:
        item = _listing(row)
        if not item:
            continue
        if any(value and (item[field] or '').casefold() != value.casefold() for field, value in [('intent',intent), ('category',category), ('state',state), ('district',district), ('shop_id',shop_id)]):
            continue
        if q and q.casefold() not in (item['title'] + ' ' + item['description']).casefold():
            continue
        if offers_only and not item['offer_active']:
            continue
        result.append(item)
    return {'status': 'ok' if result else 'not_found', 'records': result[offset:offset+limit], 'total': len(result),
            'limit': limit, 'offset': offset, 'message': 'Listing prices are submitted asking prices/budgets, not official mandi observations or guaranteed transactions.'}


@router.get('/listings')
def listings(intent: Literal['buy', 'sell'] | None = None, category: Category | None = None,
             q: str | None = Query(default=None, max_length=100),
             state: str | None = Query(default=None, max_length=100), district: str | None = Query(default=None, max_length=100),
             shop_id: str | None = Query(default=None, max_length=36),
             offers_only: bool = False, limit: int = Query(default=20, ge=1, le=100), offset: int = Query(default=0, ge=0)):
    return find_listings(intent, category, q, state, district, shop_id, offers_only, limit, offset)


@router.get('/offers')
def offers(category: Category | None = None, district: str | None = Query(default=None, max_length=100),
           limit: int = Query(default=20, ge=1, le=100), offset: int = Query(default=0, ge=0)):
    return find_listings(intent='sell', category=category, district=district, offers_only=True, limit=limit, offset=offset)


@router.delete('/listings/{listing_id}', dependencies=[Depends(require_admin)])
def withdraw_listing(listing_id: str):
    with database() as db:
        if not db.execute('UPDATE listings SET active = 0 WHERE id = ?', (listing_id,)).rowcount:
            raise HTTPException(404, 'Listing not found.')
    return {'status': 'withdrawn'}
