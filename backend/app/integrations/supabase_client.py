"""
Supabase integration client.
Uses the SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY from environment.
"""
import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

supabase: Client | None = None

def get_supabase() -> Client:
    global supabase
    if supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise RuntimeError("SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set in .env")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase
