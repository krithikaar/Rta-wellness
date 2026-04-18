import pandas as pd
from supabase import create_client, Client
import streamlit as st

# Initialize Supabase Client
def get_supabase_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    client = create_client(url, key)
    # Restore the auth session using Streamlit state to prevent hot-reload Row-Level Security failures!
    if 'access_token' in st.session_state and 'refresh_token' in st.session_state:
        try:
            client.auth.set_session(st.session_state.access_token, st.session_state.refresh_token)
        except Exception:
            pass
    return client

def upsert_daily_log(user_id, log_date, new_data):
    """
    Saves or updates a daily log entry by merging new data into the existing JSONB.
    Ensures exactly one row per user per day.
    """
    supabase = get_supabase_client()
    
    # 1. Fetch current data to perform a merge (Supabase upsert overwrites the whole JSONB column)
    res = supabase.table("health_logs").select("data").eq("user_id", user_id).eq("log_date", str(log_date)).execute()
    
    current_data = {}
    if res.data:
        current_data = res.data[0].get('data', {})
    
    # 2. Merge new entries
    current_data.update(new_data)
    
    # 3. Perform Upsert
    log_entry = {
        "user_id": user_id,
        "log_date": str(log_date),
        "data": current_data
    }
    
    result = supabase.table("health_logs").upsert(log_entry, on_conflict="user_id, log_date").execute()
    
    # Invalidate cache on new save
    st.cache_data.clear()
    return result

def get_daily_logs(user_id):
    """
    Fetches all daily logs for a specific user and returns as a flattened DataFrame.
    """
    supabase = get_supabase_client()
    result = supabase.table("health_logs").select("*").eq("user_id", user_id).execute()
    
    if not result.data:
        return pd.DataFrame()
    
    # Flatten JSONB 'data' field into columns for Pandas
    flat_data = []
    for row in result.data:
        entry = {
            "log_date": row["log_date"],
            "created_at": row["created_at"]
        }
        entry.update(row["data"])
        flat_data.append(entry)
        
    df = pd.DataFrame(flat_data)
    if "log_date" in df.columns:
        df["log_date"] = pd.to_datetime(df["log_date"])
    
    # Ensure weight columns exist for the graph even if empty
    for col in ['pre_weight', 'post_weight']:
        if col not in df.columns:
            df[col] = None
            
    return df

def get_daily_log(user_id, log_date):
    """
    Fetches the single unified log for a specific user and date.
    """
    supabase = get_supabase_client()
    res = supabase.table("health_logs").select("data").eq("user_id", user_id).eq("log_date", str(log_date)).execute()
    
    if not res.data:
        return {}
        
    entry = res.data[0]["data"]
    entry["log_date"] = str(log_date)
    return entry
