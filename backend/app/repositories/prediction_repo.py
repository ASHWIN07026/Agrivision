"""
Repository for saving and retrieving prediction logs from Supabase.
"""
from app.integrations.supabase_client import get_supabase
import json

def save_prediction(module: str, input_data: dict, result: dict, confidence: float = None):
    try:
        client = get_supabase()
        client.table("prediction_logs").insert({
            "module": module,
            "input_data": json.dumps(input_data),
            "result": json.dumps(result),
            "confidence": confidence,
        }).execute()
    except Exception as e:
        print(f"[repo] Could not save prediction log: {e}")

def get_recent_predictions(limit: int = 20):
    try:
        client = get_supabase()
        res = client.table("prediction_logs").select("*").order("created_at", desc=True).limit(limit).execute()
        return res.data
    except Exception as e:
        print(f"[repo] Could not fetch prediction logs: {e}")
        return []
