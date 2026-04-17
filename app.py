import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import streamlit_authenticator as stauth
from database import get_supabase_client, save_health_log, get_health_logs, get_latest_log
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

# --- Authentication ---
# Removed 'user' initialization from here as it's handled above with cookies

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
                res = supabase.auth.sign_up({"email": email, "password": password, "options": {"data": {"full_name": name}}})
                if res.session:
                    st.session_state.access_token = res.session.access_token
                    st.session_state.refresh_token = res.session.refresh_token
                st.success("Account created! Please check your email for verification (if enabled) or login now.")
                st.session_state.auth_mode = 'login'
                st.rerun()
            except Exception as e:
                st.error(f"Signup failed: {e}")
    
    col_link = st.columns([1,2,1])
    with col_link[1]:
        if st.button("Already have an account? Login", use_container_width=True):
            st.session_state.auth_mode = 'login'
            st.rerun()

if st.session_state.user is None:
    if 'auth_mode' not in st.session_state:
        st.session_state.auth_mode = 'login'
    
    if st.session_state.auth_mode == 'login':
        handle_login()
    else:
        handle_signup()
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
    st.markdown("**Activity Score:** A cumulative snapshot of your daily logging habits. It simply adds up your manually tracked active parameters (Water in Liters, Sleep in Hours, and your qualitative Stress level) into a single holistic indicator.")

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
    if st.button("DAILY LOG", use_container_width=True): navigate_to('daily_log')
    if st.button("PROFILE", use_container_width=True): navigate_to('profile')
    if st.button("LOGOUT", use_container_width=True):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()

elif st.session_state.page == 'dashboard':
    show_nav_row(left_page='home', right_page='daily_log', show_calendar=False)
    st.markdown("<h3 style='text-align:center;'>Weekly Overview</h3>", unsafe_allow_html=True)
    
    # Week Slider
    monday = get_monday(date.today()) + timedelta(weeks=st.session_state.week_offset)
    days = [monday + timedelta(days=i) for i in range(7)]
    labels = ["M", "T", "W", "T", "F", "S", "S"]
    col_w1, col_w2, col_w3 = st.columns([1, 10, 1], vertical_alignment="bottom")
    with col_w1:
        st.markdown('<div class="week-nav-proxy"></div>', unsafe_allow_html=True)
        if st.button("", icon=":material/keyboard_double_arrow_left:", key="w_prev", type="tertiary", help="Prev Week"):
            st.session_state.week_offset -= 1
            st.rerun()
    with col_w3:
        st.markdown('<div class="week-nav-proxy"></div>', unsafe_allow_html=True)
        if st.button("", icon=":material/keyboard_double_arrow_right:", key="w_next", type="tertiary", help="Next Week"):
            st.session_state.week_offset += 1
            st.rerun()
    
    with col_w2:
        day_cols = st.columns(7)
        for i, d in enumerate(days):
            with day_cols[i]:
                is_sel = d == st.session_state.selected_date
                if st.button(labels[i], key=f"d_btn_{i}", type="primary" if is_sel else "secondary", use_container_width=True):
                    st.session_state.selected_date = d
                    st.rerun()
                st.markdown(f"<p style='text-align:center; font-size:0.7rem; margin-top:-5px;'>{d.day}</p>", unsafe_allow_html=True)

    st.markdown(f"<h4 style='text-align:center;'>{st.session_state.selected_date.strftime('%b %d, %Y')}</h4>", unsafe_allow_html=True)
    df_w = get_health_logs(user_id, 'weight')
    fig = go.Figure()
    if not df_w.empty:
        # Sort by date for proper line connection
        if 'log_date' in df_w.columns:
            df_w = df_w.sort_values(by='log_date')
            df_w['date_str'] = df_w['log_date'].dt.strftime('%b %d')
            fig.add_trace(go.Scatter(x=df_w['date_str'], y=df_w['pre_weight'], mode='lines+markers', name='Pre-Gym', line=dict(color='#008080', width=3), marker=dict(size=8)))
            if 'post_weight' in df_w.columns:
                 fig.add_trace(go.Scatter(x=df_w['date_str'], y=df_w['post_weight'], mode='lines+markers', name='Post-Gym', line=dict(color='#20B2AA', width=3), marker=dict(size=8)))
    fig.update_layout(height=220, margin=dict(l=0,r=0,t=30,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      xaxis=dict(type='category', showgrid=False), yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)'))
    st.plotly_chart(fig, use_container_width=True)
    
    card_begin()
    c1, c2, c3 = st.columns(3)
    
    user_height_cm = st.session_state.user.user_metadata.get('height')
    w_entry = get_latest_log(user_id, 'weight', st.session_state.selected_date)
    f_entry = get_latest_log(user_id, 'food', st.session_state.selected_date)
    a_entry = get_latest_log(user_id, 'activity', st.session_state.selected_date)
    
    current_bmi = "--"
    if w_entry and user_height_cm:
        h_m = float(user_height_cm) / 100
        w_kg = float(w_entry.get('pre_weight', 0))
        if h_m > 0 and w_kg > 0:
            bmi = w_kg / (h_m * h_m)
            current_bmi = f"{bmi:.1f}"
            
    total_kcal = "--"
    if f_entry:
        total_kcal = str(int(f_entry.get('calories', 0)))
        
    activity_score = "--"
    if a_entry:
        water = float(a_entry.get('water', 0))
        sleep = float(a_entry.get('sleep_duration', 0))
        stress = float(a_entry.get('stress', 0))
        # Cumulative score from the 3 sliders
        activity_score = str(int(water + sleep + stress))
            
    c1.metric("Current BMI", current_bmi)
    c2.metric("Total Kcal", total_kcal)
    c3.metric("Activity Score", activity_score)
    card_end()
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.button("what does it mean?", type="tertiary", use_container_width=True, help="Metrics Info"):
            show_metrics_info()

elif st.session_state.page == 'daily_log':
    show_nav_row(left_page='dashboard', right_page='weight')
    st.markdown("<h3 style='text-align:center;'>Daily Log</h3>", unsafe_allow_html=True)
    if st.button("WEIGHT", use_container_width=True): navigate_to('weight')
    if st.button("FOOD DIARY", use_container_width=True): navigate_to('food')
    if st.button("ACTIVITY", use_container_width=True): navigate_to('activity')

elif st.session_state.page == 'weight':
    show_nav_row(left_page='daily_log', right_page='food', show_calendar=True)
    st.markdown(f'<p class="date-header">{st.session_state.selected_date.strftime("%B %d, %Y")}</p>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>Weight Logger</h3>", unsafe_allow_html=True)
    
    existing = get_latest_log(user_id, 'weight', st.session_state.selected_date)
    card_begin()
    colw1, colw2 = st.columns(2)
    pre_w = colw1.number_input("Pre-Gym (kg)", min_value=0.0, step=0.1, value=float(existing.get('pre_weight', 0.0)) if existing else 0.0)
    post_w = colw2.number_input("Post-Gym (kg)", min_value=0.0, step=0.1, value=float(existing.get('post_weight', 0.0)) if existing else 0.0)
    if st.button("SAVE ENTRY", use_container_width=True):
        save_health_log(user_id, st.session_state.selected_date, 'weight', {"pre_weight": pre_w, "post_weight": post_w})
        st.success("Log Saved")
    card_end()

elif st.session_state.page == 'food':
    show_nav_row(left_page='weight', right_page='activity', show_calendar=True)
    st.markdown(f'<p class="date-header">{st.session_state.selected_date.strftime("%B %d, %Y")}</p>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>Food Diary</h3>", unsafe_allow_html=True)
    
    existing = get_latest_log(user_id, 'food', st.session_state.selected_date)
    card_begin()
    f_text = st.text_area("What did you have?", value=existing.get('raw_text', "") if existing else "", height=150)
    if st.button("ANALYZE & SAVE", use_container_width=True):
        with st.spinner("Analyzing..."):
            nutrition = analyze_food(f_text)
            save_health_log(user_id, st.session_state.selected_date, 'food', {
                "raw_text": f_text,
                "time": datetime.now().strftime("%I:%M %p"),
                **nutrition
            })
            st.rerun()
    card_end()
    if existing:
        card_begin()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Kcal", int(existing.get('calories', 0)))
        c2.metric("P", f"{int(existing.get('protein', 0))}g")
        c3.metric("C", f"{int(existing.get('carbs', 0))}g")
        c4.metric("F", f"{int(existing.get('fats', 0))}g")
        card_end()
        
        micros_text = existing.get('micros', '')
        if micros_text:
            st.markdown(f"<p style='text-align:center; color:#888; font-size:0.85rem; margin-top:8px;'>{micros_text}</p>", unsafe_allow_html=True)

elif st.session_state.page == 'activity':
    show_nav_row(left_page='food', right_page='dashboard', show_calendar=True)
    st.markdown(f'<p class="date-header">{st.session_state.selected_date.strftime("%B %d, %Y")}</p>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>Activity</h3>", unsafe_allow_html=True)
    
    curr = get_latest_log(user_id, 'activity', st.session_state.selected_date) or {}
    card_begin()
    water = st.slider("Water (L)", 0.0, 10.0, float(curr.get('water', 2.0)), 0.5)
    sleep = st.slider("Sleep (Hrs)", 0.0, 16.0, float(curr.get('sleep_duration', 7.0)), 0.5)
    stress = st.slider("Stress (1-10)", 1, 10, int(curr.get('stress', 3)))
    if st.button("SAVE ACTIVITY", use_container_width=True):
        save_health_log(user_id, st.session_state.selected_date, 'activity', {
            "water": water,
            "sleep_duration": sleep,
            "sleep_quality": 7,
            "stress": stress
        })
        st.success("Activity Logged")
    card_end()
