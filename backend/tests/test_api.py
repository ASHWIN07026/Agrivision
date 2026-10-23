"""Integration regressions using the unchanged, real disease and yield artifacts."""
import io
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from PIL import Image
from app.main import app
from app.services.image_validation import ValidatorUnavailable

ROOT = Path(__file__).resolve().parents[2]


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def post_image(self, image, crop='tomato'):
        return self.client.post('/api/disease/predict', data={'crop': crop}, files={'file': ('photo.jpg', image, 'image/jpeg')})

    def test_health_and_readiness(self):
        self.assertEqual(self.client.get('/api/ready').status_code, 200)
        self.assertTrue(self.client.get('/api/health').json()['leaf_validator_available'])

    def test_account_config_endpoint_removed(self):
        response = self.client.get('/api/public-config')
        self.assertEqual(response.status_code, 404)
        self.assertNotIn('supabase_publishable_key', response.text)

    def test_supported_leaves_preserve_predictions(self):
        for crop, sample, label in [
            ('tomato', 'tomato_healthy.jpg', 'Tomato___healthy'),
            ('potato', 'potato_early_blight.jpg', 'Potato___Early_blight'),
            ('pepper', 'pepper_bacterial_spot.jpg', 'Pepper,_bell___Bacterial_spot'),
        ]:
            with self.subTest(crop=crop):
                response = self.post_image((ROOT / 'samples' / sample).read_bytes(), crop)
                self.assertEqual(response.status_code, 200, response.text)
                self.assertEqual(response.json()['disease'], label)

    def test_automatic_crop_and_default(self):
        for crop, sample in [('tomato', 'tomato_healthy.jpg'), ('potato', 'potato_early_blight.jpg'), ('pepper', 'pepper_bacterial_spot.jpg')]:
            image = (ROOT / 'samples' / sample).read_bytes()
            response = self.post_image(image, 'auto')
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.json()['crop'], crop)
        response = self.client.post('/api/disease/predict', files={'file': ('photo.jpg', image, 'image/jpeg')})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()['crop'], 'pepper')

    def assert_no_prediction(self, response):
        self.assertGreaterEqual(response.status_code, 400)
        self.assertNotIn('disease', response.json())
        self.assertNotIn('confidence', response.json())

    def test_corrupt_empty_and_oversize(self):
        for data in [b'', b'not an image', b'x' * (10 * 1024 * 1024 + 1)]:
            self.assert_no_prediction(self.post_image(data))

    def test_flat_images_rejected_before_disease_inference(self):
        for color in ['green', 'red', 'white', 'black']:
            buffer = io.BytesIO(); Image.new('RGB', (224, 224), color).save(buffer, format='PNG')
            with patch('app.main.get_disease_model') as loader:
                self.assert_no_prediction(self.post_image(buffer.getvalue()))
                loader.return_value.predict.assert_not_called()

    def test_unavailable_validator_fails_closed(self):
        with patch('app.main.validate_leaf_candidate', side_effect=ValidatorUnavailable('Unavailable')):
            response = self.post_image((ROOT / 'samples/tomato_healthy.jpg').read_bytes())
        self.assertEqual(response.status_code, 503)
        self.assert_no_prediction(response)

    def test_crop_mismatch_and_unsupported_crop(self):
        image = (ROOT / 'samples/tomato_healthy.jpg').read_bytes()
        self.assert_no_prediction(self.post_image(image, 'potato'))
        self.assert_no_prediction(self.post_image(image, 'banana'))

    def test_real_negative_photos(self):
        # Supply independent fixtures to exercise semantic rejection, not mocked decisions.
        directory = os.environ.get('AGRIVISION_NEGATIVE_FIXTURES')
        if not directory:
            self.skipTest('Set AGRIVISION_NEGATIVE_FIXTURES to downloaded person/cat/bus fixtures')
        for filename in ['person.png', 'cat.png', 'bus.jpg']:
            with self.subTest(filename=filename), patch('app.main.get_disease_model') as loader:
                response = self.post_image((Path(directory) / filename).read_bytes(), 'auto')
                self.assertEqual(response.status_code, 422, response.text)
                self.assert_no_prediction(response)
                loader.return_value.predict.assert_not_called()

    def test_yield_real_prediction_and_invalid_inputs(self):
        response = self.client.post('/api/yield/predict', data={'country': 'India', 'crop': 'Potatoes', 'year': 2026})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertGreater(response.json()['expected_yield_kg_per_hectare'], 0)
        for update in [{'country':'Atlantis'}, {'crop':'not a crop'}, {'year':1900}]:
            data = {'country':'India', 'crop':'Potatoes', 'year':2026, **update}
            self.assertEqual(self.client.post('/api/yield/predict',data=data).status_code,422)

    def test_market_key_not_configured(self):
        with patch.dict(os.environ, {'DATA_GOV_IN_API_KEY':''}):
            response = self.client.get('/api/market/price?crop=Tomato')
        self.assertEqual(response.status_code,503)
        self.assertEqual(response.json()['code'],'market_api_not_configured')
        self.assertNotIn('records',response.json())
