from copy import deepcopy
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.marketplace import router, database

KEY = 'test-only-administrator-key-0123456789'


class MarketplaceTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.environment = patch.dict(os.environ, {'MARKETPLACE_ADMIN_KEY': KEY, 'MARKETPLACE_DB_PATH': str(Path(self.directory.name) / 'market.sqlite3')})
        self.environment.start()
        self.app = FastAPI(); self.app.include_router(router)
        self.client = TestClient(self.app)
        self.headers = {'Authorization': f'Bearer {KEY}'}
        self.future = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        self.listing = dict(intent='sell', category='seeds', title='Test seed listing', description='Fixture only, not a live product.',
                            price_inr='125.50', unit='packet', quantity='5', district='Tiruppur', state='Tamil Nadu',
                            contact=dict(name='Test seller', phone='+910000000000', public_contact_consent=True))
        self.shop = dict(name='Fixture agricultural shop', categories=['seeds', 'tools'], address='Test-only address',
                         district='Tiruppur', state='Tamil Nadu', latitude=11.1, longitude=77.3,
                         contact=self.listing['contact'])

    def tearDown(self):
        self.environment.stop(); self.directory.cleanup()

    def publish(self, data=None):
        return self.client.post('/api/marketplace/listings', json=data or self.listing, headers=self.headers)

    def test_initial_results_are_empty(self):
        response = self.client.get('/api/marketplace/listings').json()
        self.assertEqual(response['records'], [])
        self.assertEqual(response['status'], 'not_found')
        self.assertFalse(self.client.get('/api/marketplace/options').json()['checkout_available'])

    def test_publishing_requires_key_and_configuration(self):
        for headers in [{}, {'Authorization':'Bearer wrong'}]:
            self.assertEqual(self.client.post('/api/marketplace/listings', json=self.listing, headers=headers).status_code,401)
        with patch.dict(os.environ, {'MARKETPLACE_ADMIN_KEY':''}):
            self.assertEqual(self.publish().status_code,503)
        with patch.dict(os.environ, {'RENDER':'true', 'MARKETPLACE_DB_PATH':''}):
            self.assertEqual(self.publish().status_code,503)

    def test_publish_read_filter_and_persistence(self):
        response = self.publish(); self.assertEqual(response.status_code,201,response.text)
        records = self.client.get('/api/marketplace/listings?category=seeds&district=tiruppur').json()['records']
        self.assertEqual(len(records),1)
        self.assertEqual(records[0]['effective_price_inr'],'125.50')
        self.assertFalse(records[0]['verified'])
        second = TestClient(self.app)
        self.assertEqual(second.get('/api/marketplace/listings').json()['total'],1)
        for query in ['intent=buy', 'category=tools', 'q=missing', 'district=Chennai', 'shop_id=missing']:
            self.assertEqual(self.client.get('/api/marketplace/listings?' + query).json()['records'], [])

    def test_actual_offer_math_and_expiry(self):
        data = {**self.listing, 'price_inr':'100.00', 'offer_price_inr':'80.00', 'offer_expires_at':self.future}
        self.assertEqual(self.publish(data).status_code,201)
        offer = self.client.get('/api/marketplace/offers').json()['records'][0]
        self.assertEqual(offer['discount_percent'],'20.00')
        self.assertEqual(offer['effective_price_inr'],'80.00')
        after_expiry = datetime.now(timezone.utc) + timedelta(days=2)
        with patch('app.api.marketplace.utcnow',return_value=after_expiry):
            self.assertEqual(self.client.get('/api/marketplace/offers').json()['records'],[])
            item = self.client.get('/api/marketplace/listings').json()['records'][0]
            self.assertEqual(item['effective_price_inr'],'100.00')
            self.assertFalse(item['offer_active'])

    def test_invalid_offers_and_inputs(self):
        for updates in [dict(category='electronics'), dict(price_inr='NaN'),dict(price_inr='1.001'),dict(price_inr='0'),
                        dict(quantity='-1'),dict(offer_price_inr='90'),dict(offer_price_inr='150',offer_expires_at=self.future),
                        dict(intent='buy',offer_price_inr='90',offer_expires_at=self.future),
                        dict(offer_price_inr='90',offer_expires_at='2020-01-01T00:00:00Z'),
                        dict(expires_at='2030-01-01T00:00:00'), dict(shop_id='nonexistent'),
                        dict(contact={**self.listing['contact'],'public_contact_consent':False})]:
            with self.subTest(updates=updates):
                self.assertEqual(self.publish({**self.listing,**updates}).status_code,422)

    def test_expired_and_withdrawn_listings_are_hidden(self):
        identifier = self.publish({**self.listing,'expires_at':self.future}).json()['id']
        with patch('app.api.marketplace.utcnow',return_value=datetime.now(timezone.utc)+timedelta(days=2)):
            self.assertEqual(self.client.get('/api/marketplace/listings').json()['records'],[])
        self.assertEqual(self.client.delete('/api/marketplace/listings/'+identifier).status_code,401)
        self.assertEqual(self.client.delete('/api/marketplace/listings/'+identifier,headers=self.headers).status_code,200)
        self.assertEqual(self.client.get('/api/marketplace/listings').json()['records'],[])

    def test_nearby_shops_radius_category_and_coordinates(self):
        response = self.client.post('/api/marketplace/shops',json=self.shop,headers=self.headers)
        self.assertEqual(response.status_code,201,response.text)
        self.assertEqual(self.publish({**self.listing,'shop_id':response.json()['id']}).status_code,201)
        base = '/api/marketplace/shops/nearby?latitude=11.1&longitude=77.3'
        shop = self.client.get(base).json()['records'][0]
        self.assertEqual(shop['distance_km'],0)
        self.assertEqual(self.client.get(base+'&category=irrigation').json()['records'],[])
        self.assertEqual(self.client.get('/api/marketplace/shops/nearby?latitude=12&longitude=78&radius_km=1').json()['records'],[])
        for query in ['latitude=91&longitude=77','latitude=nan&longitude=77', 'latitude=11&longitude=181', 'latitude=11&longitude=77&radius_km=-1']:
            self.assertEqual(self.client.get('/api/marketplace/shops/nearby?'+query).status_code,422)

    def test_phone_and_website_validation(self):
        for changes in [dict(website='javascript:alert(1)'),dict(website='http://example.com'),dict(categories=['electronics']),dict(latitude=91)]:
            self.assertEqual(self.client.post('/api/marketplace/shops',json={**self.shop,**changes},headers=self.headers).status_code,422)

    def test_pagination_and_literal_search(self):
        self.publish()
        self.publish({**self.listing,'title':'Second test product','intent':'buy'})
        self.assertEqual(len(self.client.get('/api/marketplace/listings?limit=1').json()['records']),1)
        self.assertEqual(len(self.client.get('/api/marketplace/listings?limit=1&offset=1').json()['records']),1)
        self.assertEqual(self.client.get('/api/marketplace/listings?q=%27%20OR%201=1').json()['records'],[])
        self.assertEqual(self.client.get('/api/marketplace/listings?intent=buy').json()['total'],1)
