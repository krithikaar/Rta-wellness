import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from database import get_supabase_client, upsert_daily_log, get_daily_logs, get_daily_log
from styles import apply_styles, card_begin, card_end
from api_service import analyze_food

# Supabase Client
supabase = get_supabase_client()

# Initialize
st.set_page_config(page_title="Rta Wellness", page_icon="assets/logo.svg", layout="centered")
apply_styles()

# --- Session State ---
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = date.today()
if 'week_offset' not in st.session_state:
    st.session_state.week_offset = 0
# Flags for post-save success messages
if 'show_weight_success' not in st.session_state:
    st.session_state.show_weight_success = False
if 'show_food_success' not in st.session_state:
    st.session_state.show_food_success = False
if 'show_activity_success' not in st.session_state:
    st.session_state.show_activity_success = False

# --- Navigation Helpers ---
def navigate_to(page):
    st.session_state.page = page
    st.rerun()

def get_monday(d):
    return d - timedelta(days=d.weekday())

def show_nav_row(left_page=None, right_page=None, show_calendar=False):
    import base64
    cols = st.columns([1, 4, 1, 4, 1])
    with cols[0]:
        if left_page:
            if st.button("", icon=":material/chevron_left:", key=f"nav_l_{st.session_state.page}", help="Back"):
                navigate_to(left_page)
    with cols[2]:
        if show_calendar:
            with st.popover("", icon=":material/calendar_month:", help="Select Date"):
                new_date = st.date_input("Select Date", value=st.session_state.selected_date, key=f"cal_{st.session_state.page}")
                if new_date != st.session_state.selected_date:
                    st.session_state.selected_date = new_date
                    st.rerun()
    with cols[4]:
        if right_page:
            if st.button("", icon=":material/chevron_right:", key=f"nav_r_{st.session_state.page}", help="Forward"):
                navigate_to(right_page)

# --- Date Picker Callback ---
def on_date_change(key):
    """Callback to sync date from any tab's picker into session state."""
    new_date = st.session_state[key]
    if new_date != st.session_state.selected_date:
        st.session_state.selected_date = new_date

def render_date_picker(tab_key):
    """Renders the centered calendar popover + date display for a given tab."""
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown('<div class="cal-nav-proxy"></div>', unsafe_allow_html=True)
        with st.popover("", icon=":material/calendar_month:", help="Select Date", use_container_width=True):
            st.date_input(
                "Select Date",
                value=st.session_state.selected_date,
                key=tab_key,
                on_change=on_date_change,
                args=(tab_key,)
            )
    # Always shows the current session_state date — updates immediately on callback
    st.markdown(
        f"<h4 style='text-align:center; margin-top:-10px;'>"
        f"{st.session_state.selected_date.strftime('%b %d, %Y')}</h4>",
        unsafe_allow_html=True
    )

# --- Authentication ---
def handle_login():
    col_logo_1, col_logo_2, col_logo_3 = st.columns([1,1.5,1])
    with col_logo_2:
        st.image("assets/logo.svg", use_container_width=True)
    st.markdown("<h2 style='text-align:center; margin-top:-20px;'>Join Rta Wellness</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color: #666; margin-top:-10px; margin-bottom:20px;'>Track your daily rhythm</p>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", use_container_width=True)
        if submit:
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = res.user
                st.session_state.access_token = res.session.access_token
                st.session_state.refresh_token = res.session.refresh_token
                st.rerun()
            except Exception as e:
                st.error(f"Login failed: {e}")
    
    col_link = st.columns([1,2,1])
    with col_link[1]:
        if st.button("New here? Sign Up", use_container_width=True):
            st.session_state.auth_mode = 'signup'
            st.rerun()

def handle_signup():
    col_logo_1, col_logo_2, col_logo_3 = st.columns([1,1.5,1])
    with col_logo_2:
        st.image("assets/logo.svg", use_container_width=True)
    st.markdown("<h2 style='text-align:center; margin-top:-20px;'>Join Rta Wellness</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color: #666; margin-top:-10px; margin-bottom:20px;'>Track your daily rhythm</p>", unsafe_allow_html=True)
    
    with st.form("signup_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        name = st.text_input("Name")
        submit = st.form_submit_button("Create Account", use_container_width=True)
        if submit:
            try:
                res = supabase.auth.sign_up({
                    "email": email, 
                    "password": password, 
                    "options": {"data": {"full_name": name}}
                })
                if res.session:
                    st.session_state.user = res.user
                    st.session_state.access_token = res.session.access_token
                    st.session_state.refresh_token = res.session.refresh_token
                    st.rerun()
                else:
                    st.session_state.auth_mode = 'verify_email'
                    st.rerun()
            except Exception as e:
                st.error(f"Signup failed: {e}")
    
    col_link = st.columns([1,2,1])
    with col_link[1]:
        if st.button("Already have an account? Login", use_container_width=True):
            st.session_state.auth_mode = 'login'
            st.rerun()

def handle_verify_email():
    col_logo_1, col_logo_2, col_logo_3 = st.columns([1,1.5,1])
    with col_logo_2:
        st.image("assets/logo.svg", use_container_width=True)
    st.markdown("<h2 style='text-align:center; margin-top:-20px;'>Check your email</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color: #666; margin-top:-10px; margin-bottom:20px;'>We've sent a verification link to your inbox. Please click it to activate your account and then return here to login.</p>", unsafe_allow_html=True)
    
    col_link = st.columns([1,2,1])
    with col_link[1]:
        if st.button("Back to Login", use_container_width=True):
            st.session_state.auth_mode = 'login'
            st.rerun()

if st.session_state.user is None:
    if 'auth_mode' not in st.session_state:
        st.session_state.auth_mode = 'login'
    
    if st.session_state.auth_mode == 'login':
        handle_login()
    elif st.session_state.auth_mode == 'signup':
        handle_signup()
    else:
        handle_verify_email()
    st.stop()

# User ID from Supabase
user_id = st.session_state.user.id
user_name = st.session_state.user.user_metadata.get('full_name', 'User')
is_onboarded = st.session_state.user.user_metadata.get('onboarded', False)

if not is_onboarded and st.session_state.page != 'profile':
    st.session_state.page = 'onboarding'

def handle_profile(is_onboarding=False):
    if is_onboarding:
        col_logo_1, col_logo_2, col_logo_3 = st.columns([1,1.5,1])
        with col_logo_2:
            st.image("assets/logo.svg", use_container_width=True)
        st.markdown("<h2 style='text-align:center; margin-top:-20px;'>Welcome to Rta Wellness</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color: #666; margin-top:-10px; margin-bottom:20px;'>Let's set up your baseline.</p>", unsafe_allow_html=True)
    else:
        show_nav_row(left_page='home', right_page=None)
        st.markdown("<h3 style='text-align:center; margin-top:20px;'>Your Profile</h3>", unsafe_allow_html=True)

    curr_age = st.session_state.user.user_metadata.get('age', 25)
    curr_gender = st.session_state.user.user_metadata.get('gender', 'Female')
    curr_height = st.session_state.user.user_metadata.get('height', 165)
    
    with st.form("profile_form"):
        age = st.number_input("Age", min_value=1, max_value=120, value=int(curr_age))
        gender_opts = ["Female", "Male", "Other"]
        gender = st.selectbox("Gender", gender_opts, index=gender_opts.index(curr_gender) if curr_gender in gender_opts else 0)
        height = st.number_input("Height (cm)", min_value=50, max_value=300, value=int(curr_height))
        
        submit_btn_txt = "Complete Setup" if is_onboarding else "Update Profile"
        submit = st.form_submit_button(submit_btn_txt, use_container_width=True)
        
        if submit:
            try:
                res = supabase.auth.update_user({
                    "data": {
                        "age": age,
                        "gender": gender,
                        "height": height,
                        "onboarded": True
                    }
                })
                st.session_state.user = res.user
                if is_onboarding:
                    st.session_state.page = 'home'
                else:
                    st.success("Profile Updated!")
                st.rerun()
            except Exception as e:
                st.error(f"Error updating profile: {e}")

# --- Overlay Dialogs ---
@st.dialog("What do these metrics mean?")
def show_metrics_info():
    st.markdown("**Current BMI:** Body Mass Index is a simple measure of body fat based on your weight and height. Normal healthy values typically range between **18.5** and **24.9**.")
    st.markdown("**Total Kcal:** This is the total sum of the calorie intake you've logged today. General daily targets often sit around **2,000 kcal** for adult females and **2,500 kcal** for adult males, though your personal targets may vary.")
    st.markdown("**Activity Score:** A cumulative snapshot of your daily logging habits. It simply adds up your manually tracked active parameters (Water in Liters, Sleep Quality, Stress, Muscle Soreness, and Workout Intensity) into a single holistic indicator.")

# --- Page Content ---
if st.session_state.page == 'onboarding':
    handle_profile(is_onboarding=True)

elif st.session_state.page == 'profile':
    handle_profile(is_onboarding=False)

elif st.session_state.page == 'home':
    col_logo_1, col_logo_2, col_logo_3 = st.columns([1,2,1])
    with col_logo_2:
        st.image("assets/logo.svg", use_container_width=True)
    st.markdown('<p class="cycles-title">Cycles of Self</p>', unsafe_allow_html=True)
    
    if st.button("DASHBOARD", use_container_width=True): navigate_to('dashboard')
    if st.button("PROFILE", use_container_width=True): navigate_to('profile')
    if st.button("LOGOUT", use_container_width=True):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()

elif st.session_state.page == 'dashboard':
    show_nav_row(left_page='home', right_page=None)
    
    tab_stats, tab_weight, tab_food, tab_activity = st.tabs(["Stats", "Weight", "Food", "Activity"])
    
    # ── STATS TAB ──────────────────────────────────────────────────
    with tab_stats:
        render_date_picker("stats_date_picker")
        
        # Slider for range
        graph_range = st.select_slider(
            "Select Range",
            options=["Weekly", "Monthly", "All Time"],
            value="Weekly",
            label_visibility="collapsed",
            key="graph_range_main"
        )
        
        # Fetch Data for selected date (always fresh — no cache)
        daily_data = get_daily_log(user_id, st.session_state.selected_date)
        
        # Weight Graph
        df_w = get_daily_logs(user_id)
        today = date.today()
        if not df_w.empty:
            if graph_range == "Weekly":
                df_w = df_w[df_w['log_date'].dt.date >= (today - timedelta(days=7))]
            elif graph_range == "Monthly":
                df_w = df_w[df_w['log_date'].dt.date >= (today - timedelta(days=30))]
            
            df_w = df_w.sort_values(by='log_date')
            df_w['date_str'] = df_w['log_date'].dt.strftime('%b %d')
            
        fig = go.Figure()
        if not df_w.empty:
            df_plot = df_w.copy()
            
            if 'pre_weight' in df_plot.columns:
                df_plot['p_w_num'] = pd.to_numeric(df_plot['pre_weight'], errors='coerce')
                df_valid = df_plot.dropna(subset=['p_w_num'])
                if not df_valid.empty:
                    fig.add_trace(go.Scatter(x=df_valid['date_str'], y=df_valid['p_w_num'], mode='lines+markers', name='Pre-Gym', line=dict(color='#008080', width=3)))
            
            if 'post_weight' in df_plot.columns:
                df_plot['po_w_num'] = pd.to_numeric(df_plot['post_weight'], errors='coerce')
                df_valid = df_plot.dropna(subset=['po_w_num'])
                if not df_valid.empty:
                    fig.add_trace(go.Scatter(x=df_valid['date_str'], y=df_valid['po_w_num'], mode='lines+markers', name='Post-Gym', line=dict(color='#20B2AA', width=3)))
        
        fig.update_layout(
            height=220,
            margin=dict(l=0, r=0, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(type='category', showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)', nticks=5)
        )
        st.plotly_chart(fig, use_container_width=True, key="dashboard_fig")
        
        # Metrics Card
        card_begin()
        c1, c2, c3 = st.columns(3)
        
        bmi_val = str(daily_data.get('bmi', '--'))
        
        kcal_val = "--"
        if daily_data.get('calories'):
            try:
                kcal_val = str(int(float(daily_data['calories'])))
            except (ValueError, TypeError):
                kcal_val = "--"
            
        score_val = "--"
        if daily_data.get('activity_score'):
            try:
                score_val = str(int(float(daily_data['activity_score'])))
            except (ValueError, TypeError):
                score_val = "--"
        
        c1.metric("Current BMI", bmi_val)
        c2.metric("Total Kcal", kcal_val)
        c3.metric("Activity Score", score_val)
        card_end()
        
        # "What does it mean?" button — opens the @st.dialog overlay
        col_info_1, col_info_2, col_info_3 = st.columns([1, 2, 1])
        with col_info_2:
            if st.button("what does it mean?", use_container_width=True, key="btn_metrics_info"):
                show_metrics_info()

    # ── WEIGHT TAB ─────────────────────────────────────────────────
    with tab_weight:
        render_date_picker("weight_date_picker")
        
        # Show success message from previous save
        if st.session_state.show_weight_success:
            st.success(f"✅ Weight logged successfully for {st.session_state.selected_date.strftime('%b %d, %Y')}!")
            st.session_state.show_weight_success = False
        
        # Fetch existing data for this date
        existing_data = get_daily_log(user_id, st.session_state.selected_date)
        
        card_begin()
        pre_w = st.number_input(
            "Pre-workout weight (kg)",
            min_value=0.0, step=0.1,
            value=float(existing_data.get('pre_weight', 0.0)) if existing_data else 0.0,
            format="%.1f",
            key=f"pre_w_{st.session_state.selected_date}"
        )
        post_w = st.number_input(
            "Post-workout weight (kg)",
            min_value=0.0, step=0.1,
            value=float(existing_data.get('post_weight', 0.0)) if existing_data else 0.0,
            format="%.1f",
            key=f"post_w_{st.session_state.selected_date}"
        )
        
        if st.button("SAVE WEIGHT", use_container_width=True, key="save_weight_btn"):
            user_height_cm = st.session_state.user.user_metadata.get('height')
            bmi = "--"
            try:
                if user_height_cm and float(user_height_cm) > 0 and pre_w > 0:
                    h_m = float(user_height_cm) / 100
                    bmi = round(pre_w / (h_m * h_m), 1)
            except Exception:
                bmi = "--"
            
            upsert_daily_log(user_id, st.session_state.selected_date, {
                "pre_weight": float(pre_w), 
                "post_weight": float(post_w),
                "bmi": bmi
            })
            st.session_state.show_weight_success = True
            st.rerun()
        card_end()

    # ── FOOD TAB ───────────────────────────────────────────────────
    with tab_food:
        render_date_picker("food_date_picker")
        
        # Show success message from previous save
        if st.session_state.show_food_success:
            st.success(f"✅ Food logged & analyzed successfully for {st.session_state.selected_date.strftime('%b %d, %Y')}!")
            st.session_state.show_food_success = False
        
        # Fetch existing data for this date
        existing_data = get_daily_log(user_id, st.session_state.selected_date)
        
        st.markdown("<h5 style='text-align:center; margin-bottom: 5px;'>What did you have?</h5>", unsafe_allow_html=True)
        card_begin()
        food_text = st.text_area(
            "What did you have?",
            value=existing_data.get('raw_text', '') if existing_data else '',
            height=150,
            label_visibility="collapsed",
            key=f"food_input_{st.session_state.selected_date}"
        )
        
        if st.button("ANALYZE & SAVE", use_container_width=True, key="analyze_save_btn"):
            if food_text.strip():
                with st.spinner("Analyzing with AI..."):
                    nutrition = analyze_food(food_text)
                    upsert_daily_log(user_id, st.session_state.selected_date, {
                        "raw_text": food_text,
                        "food_time": datetime.now().strftime("%I:%M %p"),
                        **nutrition
                    })
                    st.session_state.show_food_success = True
                    st.rerun()
            else:
                st.warning("Please enter some food items first.")
        card_end()
        
        # Re-fetch to display the just-saved (or already stored) nutrition data
        display_data = get_daily_log(user_id, st.session_state.selected_date)
        
        if display_data and display_data.get('calories'):
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            card_begin()
            fc1, fc2, fc3, fc4 = st.columns(4)
            fc1.metric("Kcal", int(float(display_data.get('calories', 0))))
            fc2.metric("P", f"{int(float(display_data.get('protein', 0)))}g")
            fc3.metric("C", f"{int(float(display_data.get('carbs', 0)))}g")
            fc4.metric("F", f"{int(float(display_data.get('fats', 0)))}g")
            card_end()
            
            micros = display_data.get('micros', '')
            if micros:
                st.markdown(
                    f"<p style='text-align:center; color:#888; font-size:0.85rem; margin-top:10px;'>{micros}</p>",
                    unsafe_allow_html=True
                )

    # ── ACTIVITY TAB ───────────────────────────────────────────────
    with tab_activity:
        render_date_picker("activity_date_picker")
        
        # Show success message from previous save
        if st.session_state.show_activity_success:
            st.success(f"✅ Activity logged successfully for {st.session_state.selected_date.strftime('%b %d, %Y')}!")
            st.session_state.show_activity_success = False
        
        # Fetch existing data for this date
        curr_data = get_daily_log(user_id, st.session_state.selected_date)
        
        card_begin()
        water = st.slider("Water (L)", 0.0, 10.0, float(curr_data.get('water', 2.0)), 0.5,
                          key=f"water_{st.session_state.selected_date}")
        sleep_q = st.slider("Sleep Quality (1-10)", 1, 10, int(curr_data.get('sleep_quality', 7)),
                            key=f"sleep_{st.session_state.selected_date}")
        stress = st.slider("Stress (1-10)", 1, 10, int(curr_data.get('stress', 3)),
                           key=f"stress_{st.session_state.selected_date}")
        soreness = st.slider("Muscle Soreness (1-10)", 1, 10, int(curr_data.get('soreness', 1)),
                             key=f"soreness_{st.session_state.selected_date}")
        intensity = st.slider("Workout Intensity (1-10)", 1, 10, int(curr_data.get('intensity', 5)),
                              key=f"intensity_{st.session_state.selected_date}")
        
        if st.button("SAVE ACTIVITY", use_container_width=True, key="save_activity_btn"):
            composite_score = water + sleep_q + stress + soreness + intensity
            upsert_daily_log(user_id, st.session_state.selected_date, {
                "water": water,
                "sleep_quality": sleep_q,
                "stress": stress,
                "soreness": soreness,
                "intensity": intensity,
                "activity_score": composite_score
            })
            st.session_state.show_activity_success = True
            st.rerun()
        card_end()
