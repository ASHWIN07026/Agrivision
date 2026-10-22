import io
import json
import os
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from app.services.market_service import MarketProviderError, get_market_price


class MarketServiceTests(unittest.TestCase):
    def test_missing_api_key_fails_explicitly(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(MarketProviderError) as raised:
                get_market_price("Tomato")
        self.assertEqual(raised.exception.code, "market_api_not_configured")
        self.assertEqual(raised.exception.status_code, 503)

    def test_valid_provider_record_preserves_source_fields(self):
        payload = {
            "records": [
                {
                    "commodity": "Tomato",
                    "state": "Tamil Nadu",
                    "district": "Coimbatore",
                    "market": "Pollachi",
                    "variety": "Local",
                    "arrival_date": "17/06/2026",
                    "min_price": "1800",
                    "max_price": "2400",
                    "modal_price": "2200",
                }
            ]
        }
        with (
            patch.dict(os.environ, {"DATA_GOV_IN_API_KEY": "test-key"}),
            patch(
                "app.services.market_service.urlopen",
                return_value=io.BytesIO(json.dumps(payload).encode()),
            ) as mocked_urlopen,
        ):
            result = get_market_price(
                "tomato",
                state="Tamil Nadu",
                district="Coimbatore",
                market="Pollachi",
                observed_date="2026-06-17",
            )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["records"][0]["modal_price"], 2200)
        self.assertEqual(result["records"][0]["price_unit"], "INR/quintal")
        self.assertIn("not real-time", result["records"][0]["freshness"])
        request_url = mocked_urlopen.call_args.args[0].full_url
        self.assertIn("filters%5Bcommodity%5D=Tomato", request_url)
        self.assertIn("filters%5Barrival_date%5D=17%2F06%2F2026", request_url)

    def test_empty_provider_response_returns_no_price(self):
        with (
            patch.dict(os.environ, {"DATA_GOV_IN_API_KEY": "test-key"}),
            patch(
                "app.services.market_service.urlopen",
                return_value=io.BytesIO(b'{"records": []}'),
            ),
        ):
            result = get_market_price("Potato")
        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["records"], [])

    def test_provider_rate_limit_is_not_misreported_as_no_data(self):
        rate_limit = HTTPError(
            "https://api.data.gov.in/",
            429,
            "Too Many Requests",
            {},
            io.BytesIO(),
        )
        with (
            patch.dict(os.environ, {"DATA_GOV_IN_API_KEY": "test-key"}),
            patch("app.services.market_service.urlopen", side_effect=rate_limit),
        ):
            with self.assertRaises(MarketProviderError) as raised:
                get_market_price("Tomato")
        self.assertEqual(raised.exception.code, "market_api_rate_limited")
        self.assertEqual(raised.exception.status_code, 503)

    def test_provider_authentication_failure_is_explicit(self):
        auth_error = HTTPError(
            "https://api.data.gov.in/",
            401,
            "Unauthorized",
            {},
            io.BytesIO(),
        )
        with (
            patch.dict(os.environ, {"DATA_GOV_IN_API_KEY": "test-key"}),
            patch("app.services.market_service.urlopen", side_effect=auth_error),
        ):
            with self.assertRaises(MarketProviderError) as raised:
                get_market_price("Potato")
        self.assertEqual(raised.exception.code, "market_api_authentication_failed")
        self.assertEqual(raised.exception.status_code, 503)

    def test_invalid_crop_and_date_are_rejected(self):
        with self.assertRaises(MarketProviderError) as invalid_crop:
            get_market_price("Maize")
        self.assertEqual(invalid_crop.exception.status_code, 422)

        with self.assertRaises(MarketProviderError) as invalid_date:
            get_market_price("Tomato", observed_date="17/06/2026")
        self.assertEqual(invalid_date.exception.code, "invalid_date")

    def test_invalid_prices_or_dates_are_not_displayed(self):
        from app.services.market_service import _format_record
        record = dict(commodity='Tomato', state='Tamil Nadu', district='Coimbatore',
                      market='Pollachi', arrival_date='22/10/2026',
                      min_price='100', max_price='300', modal_price='200')
        for changes in [dict(modal_price='NaN'), dict(modal_price='400'),
                        dict(min_price='-1'), dict(arrival_date='invalid')]:
            self.assertIsNone(_format_record({**record, **changes}))

    def test_malformed_provider_response(self):
        with patch.dict(os.environ, {'DATA_GOV_IN_API_KEY':'test-key'}):
            for payload in [b'not json', b'[]', b'{"records":null}']:
                with patch('app.services.market_service.urlopen', return_value=io.BytesIO(payload)):
                    with self.assertRaises(MarketProviderError):
                        get_market_price('Tomato')


if __name__ == "__main__":
    unittest.main()
