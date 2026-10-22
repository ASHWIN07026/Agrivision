import io
import json
import os
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.services import shop_provider as service


class ShopProviderTests(unittest.TestCase):
    def setUp(self):
        app = FastAPI(); app.include_router(service.router)
        self.client = TestClient(app)
        self.env = patch.dict(os.environ, {'GEOAPIFY_API_KEY':'private-test-only-key'}); self.env.start()
        service._CACHE.clear()
        self.url = '/api/shops/nearby?latitude=11.1&longitude=77.3'
        self.feature = {'properties':{'name':'Fixture farm supplies', 'place_id':'fixture-id', 'lat':11.1,'lon':77.3,
                                     'categories':['commercial','commercial.agrarian'], 'formatted':'Fixture-only address',
                                     'datasource':{'raw':{'phone':'+910000000000','website':'https://example.com','opening_hours':'Mo-Fr 09:00-17:00'}}}}

    def tearDown(self):self.env.stop();service._CACHE.clear()

    def test_missing_key_and_invalid_coordinates(self):
        with patch.dict(os.environ, {'GEOAPIFY_API_KEY':''}): self.assertEqual(self.client.get(self.url).status_code,503)
        for q in ['latitude=91&longitude=77','latitude=nan&longitude=77','latitude=11', 'town=%20%20','latitude=11&longitude=77&radius_km=100']:
            self.assertEqual(self.client.get('/api/shops/nearby?'+q).status_code,422)

    def test_mapped_records_cache_and_category(self):
        with patch.object(service,'_request',return_value=[self.feature]) as request:
            first = self.client.get(self.url); second = self.client.get(self.url)
        self.assertEqual(first.status_code,200,first.text)
        self.assertEqual(first.json()['records'][0]['name'],'Fixture farm supplies')
        self.assertEqual(first.json()['records'][0]['distance_km'],0)
        self.assertEqual(request.call_count,1)
        self.assertEqual(request.call_args.args[1]['categories'],'commercial.agrarian')
        self.assertEqual(request.call_args.args[1]['filter'],'circle:77.3,11.1,25000')
        self.assertTrue(second.json()['cached'])
        self.assertNotIn('private-test-only-key',first.text)
        self.assertNotIn('price',first.json()['records'][0])
        self.assertNotIn('discount',first.json()['records'][0])

    def test_town_geocoding(self):
        with patch.object(service,'_request',side_effect=[[{'properties':{'lat':11.1,'lon':77.3,'formatted':'Tiruppur, Tamil Nadu'}}],[self.feature]]) as request:
            response = self.client.get('/api/shops/nearby?town=Tiruppur')
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(response.json()['location_label'],'Tiruppur, Tamil Nadu')
        self.assertEqual(request.call_args_list[0].args[1]['filter'],'countrycode:in')

    def test_unmapped_or_invalid_shops_not_fabricated(self):
        for feature in [{}, {'properties':{}}, {'properties':{**self.feature['properties'],'categories':['commercial.supermarket']}},
                        {'properties':{**self.feature['properties'],'name':None}},
                        {'properties':{**self.feature['properties'],'lat':80}},
                        {'properties':{**self.feature['properties'],'lon':'not-number'}}]:
            self.assertIsNone(service._record(feature,11.1,77.3,25))
        with patch.object(service,'_request',return_value=[]):
            self.assertEqual(self.client.get(self.url).json()['records'],[])

    def test_unsafe_website_is_removed(self):
        self.feature['properties']['datasource']['raw']['website']='javascript:alert(1)'
        self.assertIsNone(service._record(self.feature,11.1,77.3,25)['website'])

    def test_provider_errors_do_not_leak_key(self):
        for code,expected in [(401,503),(403,503),(429,429),(500,503)]:
            with patch.object(service,'urlopen',side_effect=HTTPError('https://api.geoapify.com/?apiKey=secret',code,'error',{},None)):
                response=self.client.get(self.url)
            self.assertEqual(response.status_code,expected)
            self.assertNotIn('secret',response.text)
            self.assertNotIn('private-test-only-key',response.text)

    def test_bad_json_and_transport_timeout(self):
        for data in [b'not json',b'[]',b'{"features":null}',b'x'*(2*1024*1024+1)]:
            with patch.object(service,'urlopen',return_value=io.BytesIO(data)):
                self.assertEqual(self.client.get(self.url).status_code,502)
        with patch.object(service,'urlopen',side_effect=TimeoutError()):self.assertEqual(self.client.get(self.url).status_code,503)

    def test_budget_rejects_before_network(self):
        with patch.object(service,'_BUDGET_DAY',service.datetime.now(service.timezone.utc).date().isoformat()),patch.object(service,'_BUDGET_USED',2000),patch.object(service,'urlopen') as request:
            self.assertEqual(self.client.get(self.url).status_code,429)
            request.assert_not_called()
