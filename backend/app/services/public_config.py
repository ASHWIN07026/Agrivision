"""Expose only explicitly configured browser-safe Supabase credentials."""
import base64
import json
import os
from urllib.parse import urlparse


def public_config():
    url = os.environ.get('SUPABASE_URL', '').strip().rstrip('/')
    key = os.environ.get('SUPABASE_PUBLISHABLE_KEY', '').strip()
    try:
        parsed = urlparse(url)
    except ValueError:
        parsed = urlparse('')
    allowed_key = key.startswith('sb_publishable_') and len(key) > 20
    if key.count('.') == 2:
        try:
            payload = key.split('.')[1]
            claims = json.loads(base64.urlsafe_b64decode(payload + '=' * (-len(payload) % 4)))
            allowed_key = isinstance(claims, dict) and claims.get('role') == 'anon'
        except (ValueError, UnicodeError, TypeError):
            allowed_key = False
    configured = bool(parsed.scheme == 'https' and parsed.hostname and not parsed.username and not parsed.password and not parsed.query and not parsed.fragment and parsed.path in ('', '/') and allowed_key)
    return {'auth_configured': configured, 'supabase_url': url if configured else '', 'supabase_publishable_key': key if configured else ''}
