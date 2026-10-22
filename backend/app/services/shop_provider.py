"""Server-only Geoapify lookup of mapped agricultural shops; no invented stock/offers."""
from collections import OrderedDict
from datetime import datetime, timezone
import hashlib
import json
import math
import os
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix='/api/shops', tags=['Mapped agricultural shops'])
CATEGORY = 'commercial.agrarian'
_CACHE = OrderedDict()
_LOCK = threading.Lock()
_CACHE_LOCK = threading.Lock()
_BUDGET_DAY = ''
_BUDGET_USED = 0
_LAST_CALL = 0.0


def _request(endpoint, params, key):
    global _BUDGET_DAY, _BUDGET_USED, _LAST_CALL
    day = datetime.now(timezone.utc).date().isoformat()
    if day != _BUDGET_DAY:
        _BUDGET_DAY, _BUDGET_USED = day, 0
    if _BUDGET_USED >= 2000:
        raise HTTPException(429, 'The daily shop-search request budget has been reached. Try again tomorrow.')
    # Requests are serialized by _LOCK. Keep below the provider's free-plan burst rate.
    delay = .3 - (time.monotonic() - _LAST_CALL)
    if delay > 0:
        time.sleep(delay)
    _LAST_CALL = time.monotonic()
    _BUDGET_USED += 1
    params = {**params, 'apiKey': key}
    request = Request(f'https://api.geoapify.com/{endpoint}?{urlencode(params)}', headers={'Accept':'application/json'})
    try:
        with urlopen(request, timeout=10) as response:
            content = response.read(2 * 1024 * 1024 + 1)
    except HTTPError as exc:
        # Never echo the upstream URL: it contains the private key.
        if exc.code in (401, 403):
            raise HTTPException(503, 'The shop provider rejected its API key. Check the backend Geoapify key and restrictions.') from None
        if exc.code == 429:
            raise HTTPException(429, 'The shop provider quota is temporarily exhausted. Try again later.') from None
        raise HTTPException(503, 'The shop provider is unavailable. Try again later.') from None
    except (URLError, TimeoutError, OSError):
        raise HTTPException(503, 'The shop provider could not be reached. Try again later.') from None
    if len(content) > 2 * 1024 * 1024:
        raise HTTPException(502, 'The shop provider response exceeded the allowed size.')
    try:
        data = json.loads(content)
        if not isinstance(data, dict) or not isinstance(data.get('features'), list):
            raise ValueError()
        return data['features']
    except (ValueError, UnicodeDecodeError):
        raise HTTPException(502, 'The shop provider returned an invalid response.') from None


def _distance(lat1, lon1, lat2, lon2):
    p1,p2 = math.radians(lat1),math.radians(lat2)
    a=math.sin((p2-p1)/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(math.radians(lon2-lon1)/2)**2
    return 6371.0088 * 2 * math.asin(math.sqrt(min(1,max(0,a))))


def _text(value):
    return value.strip() if isinstance(value, str) and value.strip() else None


def _record(feature, latitude, longitude, radius):
    if not isinstance(feature, dict): return None
    p = feature.get('properties')
    if not isinstance(p, dict): return None
    categories = p.get('categories')
    if not isinstance(categories, list) or CATEGORY not in categories: return None
    name = _text(p.get('name'))
    lat,lon = p.get('lat'),p.get('lon')
    if not name or isinstance(lat,bool) or isinstance(lon,bool): return None
    try:
        lat,lon = float(lat),float(lon)
    except (ValueError,TypeError): return None
    if not (math.isfinite(lat) and math.isfinite(lon) and -90<=lat<=90 and -180<=lon<=180): return None
    distance = _distance(latitude, longitude, lat, lon)
    if distance > radius: return None
    raw = p.get('datasource', {}).get('raw', {}) if isinstance(p.get('datasource'),dict) else {}
    if not isinstance(raw,dict): raw = {}
    contact = p.get('contact') if isinstance(p.get('contact'),dict) else {}
    website = _text(contact.get('website')) or _text(p.get('website')) or _text(raw.get('website')) or _text(raw.get('contact:website'))
    if website:
        try:
            parsed = urlsplit(website)
            if parsed.scheme not in ('http','https') or not parsed.hostname or parsed.username or parsed.password: website = None
        except ValueError: website = None
    return {'id':str(p.get('place_id') or feature.get('id') or f'{lat},{lon}:{name}'),
            'name':name,'address':_text(p.get('formatted')),'latitude':lat,'longitude':lon,
            'distance_km':round(distance,2),'categories':categories,
            'phone':_text(contact.get('phone')) or _text(raw.get('phone')) or _text(raw.get('contact:phone')),
            'website':website, 'opening_hours':_text(raw.get('opening_hours')),
            'source':'Geoapify / OpenStreetMap','verified':False}


@router.get('/nearby')
def nearby_shops(latitude: float | None = Query(default=None,ge=-90,le=90),
                 longitude: float | None = Query(default=None,ge=-180,le=180),
                 town: str | None = Query(default=None,min_length=2,max_length=100),
                 radius_km: float = Query(default=25,ge=1,le=50,allow_inf_nan=False)):
    if (latitude is None) != (longitude is None): raise HTTPException(422, 'Provide both latitude and longitude.')
    if latitude is None and not (town and town.strip()): raise HTTPException(422, 'Provide a town or your location.')
    if latitude is not None and not all(math.isfinite(x) for x in (latitude,longitude)):
        raise HTTPException(422, 'Coordinates must be finite.')
    key = os.environ.get('GEOAPIFY_API_KEY','').strip()
    if not key: raise HTTPException(503, 'Mapped shop search is not configured. Set GEOAPIFY_API_KEY in the backend environment.')
    cache_key = (hashlib.sha256(key.encode()).hexdigest(),latitude,longitude,(town or '').strip().casefold() if latitude is None else '',radius_km)
    with _CACHE_LOCK:
        cached = _CACHE.get(cache_key)
        if cached and cached[0] > time.monotonic():
            _CACHE.move_to_end(cache_key)
            return {**cached[1], 'cached':True}
    if not _LOCK.acquire(blocking=False): raise HTTPException(429, 'Shop search is busy. Try again shortly.')
    try:
        location_label = None
        if latitude is None:
            features = _request('v1/geocode/search', {'text':town.strip(),'filter':'countrycode:in','type':'city','limit':1}, key)
            if not features:
                return {'status':'not_found','records':[],'message':'Town not found in India. Try a district or a more specific place name.',
                        'fetched_at':datetime.now(timezone.utc).isoformat(),'source':'Geoapify / OpenStreetMap','cached':False}
            try:
                props = features[0]['properties']
                latitude,longitude = float(props['lat']),float(props['lon'])
                if not (math.isfinite(latitude) and math.isfinite(longitude) and -90<=latitude<=90 and -180<=longitude<=180): raise ValueError()
                location_label = _text(props.get('formatted'))
            except (KeyError,IndexError,ValueError,TypeError):
                raise HTTPException(502, 'The location provider returned invalid coordinates.') from None
        features = _request('v2/places', {'categories':CATEGORY,'filter':f'circle:{longitude},{latitude},{int(radius_km*1000)}',
                                         'bias':f'proximity:{longitude},{latitude}','limit':20}, key)
        records = [record for feature in features if (record := _record(feature,latitude,longitude,radius_km))]
        records = list({record['id']:record for record in records}.values())
        records.sort(key=lambda r:r['distance_km'])
        result = {'status':'ok' if records else 'not_found','records':records,'source':'Geoapify / OpenStreetMap',
                  'location_label':location_label,'radius_km':radius_km,'cached':False,
                  'fetched_at':datetime.now(timezone.utc).isoformat(),
                  'message':'Mapped agricultural shops only. Coverage may be incomplete; call to confirm stock, prices, offers and opening hours.',
                  'attribution':[{'name':'Geoapify','url':'https://www.geoapify.com/'},{'name':'OpenStreetMap contributors','url':'https://www.openstreetmap.org/copyright'}]}
        with _CACHE_LOCK:
            _CACHE[cache_key] = (time.monotonic()+300,result)
            while len(_CACHE)>256: _CACHE.popitem(last=False)
        return result
    finally:
        _LOCK.release()
