import streamlit as st
from supabase import create_client, Client

# This script provides the SQL required to set up your Supabase project.
# You should run the SQL in the Supabase Dashboard SQL Editor.

SETUP_SQL = """
-- 1. Create the health_logs table
CREATE TABLE IF NOT EXISTS public.health_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) NOT NULL,
    log_date DATE NOT NULL,
    log_type TEXT NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Enable Row Level Security (RLS)
ALTER TABLE public.health_logs ENABLE ROW LEVEL SECURITY;

-- 3. Create a policy to allow users to ONLY see their own data
CREATE POLICY "Users can only see their own logs" 
ON public.health_logs 
FOR ALL 
USING (auth.uid() = user_id);

-- 4. Create an index for faster queries
CREATE INDEX IF NOT EXISTS idx_health_logs_user_date ON public.health_logs(user_id, log_date);
"""

def verify_setup():
    print("--- Supabase Setup Instructions ---")
    print("Please copy and paste the following SQL into the SQL Editor in your Supabase Dashboard:")
    print(SETUP_SQL)
    print("\n-----------------------------------")
    
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        supabase = create_client(url, key)
        
        # Test connection by listing tables (if possible)
        # Note: listing tables isn't direct via PostgREST, but we can try a dummy select
        print("Checking connection to Supabase...")
        res = supabase.table("health_logs").select("id").limit(1).execute()
        print("✅ Connection successful.")
        print("✅ health_logs table detected.")
    except Exception as e:
        print(f"❌ Setup check failed: {e}")
        print("If you haven't run the SQL above, please do so now in the Supabase Dashboard.")

if __name__ == "__main__":
    verify_setup()
