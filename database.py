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

def save_health_log(user_id, log_date, log_type, data_dict):
    """
    Saves a log entry to Supabase health_logs table.
    """
    supabase = get_supabase_client()
    log_entry = {
        "user_id": user_id,
        "log_date": str(log_date),
        "log_type": log_type,
        "data": data_dict
    }
    result = supabase.table("health_logs").insert(log_entry).execute()
    # Invalidate cache on new save
    st.cache_data.clear()
    return result

@st.cache_data
def get_health_logs(user_id, log_type=None):
    """
    Fetches logs for a specific user from Supabase.
    Can be filtered by log_type.
    """
    supabase = get_supabase_client()
    query = supabase.table("health_logs").select("*").eq("user_id", user_id)
    
    if log_type:
        query = query.eq("log_type", log_type)
        
    result = query.execute()
    
    if not result.data:
        return pd.DataFrame()
    
    # Flatten JSONB 'data' field into columns for Pandas
    flat_data = []
    for row in result.data:
        entry = {
            "id": row["id"],
            "log_date": row["log_date"],
            "log_type": row["log_type"],
            "created_at": row["created_at"]
        }
        entry.update(row["data"])
        flat_data.append(entry)
        
    df = pd.DataFrame(flat_data)
    if "log_date" in df.columns:
        df["log_date"] = pd.to_datetime(df["log_date"])
    return df

@st.cache_data
def get_latest_log(user_id, log_type, log_date=None):
    """
    Get the most recent log of a specific type for a user on a specific date.
    """
    supabase = get_supabase_client()
    query = supabase.table("health_logs").select("*").eq("user_id", user_id).eq("log_type", log_type)
    if log_date:
        query = query.eq("log_date", str(log_date))
    
    result = query.order("created_at", desc=True).limit(1).execute()
    
    if not result.data:
        return None
        
    row = result.data[0]
    entry = row["data"]
    entry["log_date"] = row["log_date"]
    return entry
