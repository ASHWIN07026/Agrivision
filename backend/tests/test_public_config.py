import base64
import json
import unittest
from unittest.mock import patch
from app.services.public_config import public_config

class PublicConfigTests(unittest.TestCase):
    def test_missing_or_privileged_credentials_are_never_exposed(self):
        for key in ['', 'sb_secret_should_never_be_exposed', self.jwt({'role': 'service_role'}), self.jwt([]), 'invalid.key.value']:
            with patch.dict('os.environ', {'SUPABASE_URL': 'https://test.supabase.co', 'SUPABASE_PUBLISHABLE_KEY': key, 'SUPABASE_SERVICE_ROLE_KEY': 'private'}, clear=True):
                result = public_config()
                self.assertFalse(result['auth_configured'])
                self.assertEqual(result['supabase_publishable_key'], '')
                self.assertNotIn('private', json.dumps(result))

    def jwt(self, claims):
        payload = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip('=')
        return 'header.' + payload + '.signature'

    def test_publishable_and_legacy_anon_are_supported(self):
        for key in ['sb_publishable_example_test_key', self.jwt({'role': 'anon'})]:
            with patch.dict('os.environ', {'SUPABASE_URL': 'https://test.supabase.co/', 'SUPABASE_PUBLISHABLE_KEY': key}, clear=True):
                result = public_config()
                self.assertTrue(result['auth_configured'])
                self.assertEqual(result['supabase_url'], 'https://test.supabase.co')
                self.assertEqual(result['supabase_publishable_key'], key)

    def test_insecure_and_credential_urls_rejected(self):
        for url in ['http://test.supabase.co', 'https://user:pass@test.supabase.co', 'https://test.supabase.co?token=secret', 'https://test.supabase.co/other']:
            with patch.dict('os.environ', {'SUPABASE_URL': url, 'SUPABASE_PUBLISHABLE_KEY': 'sb_publishable_example_test_key'}, clear=True):
                self.assertFalse(public_config()['auth_configured'])
