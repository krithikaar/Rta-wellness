import streamlit as st

def apply_styles():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');

        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Outfit', sans-serif;
            background-color: #FDFBF7;
            color: #004D4D;
        }

        /* Cycles of Self Typography */
        .cycles-title {
            text-align: center;
            font-size: 1.2rem;
            letter-spacing: 0.4rem;
            text-transform: uppercase;
            font-weight: 300;
            color: #008080;
            margin-top: -15px;
            margin-bottom: 30px;
        }

        /* Glassmorphism Cards */
        .glass-card {
            background: rgba(255, 255, 255, 0.75);
            backdrop-filter: blur(12px);
            border-radius: 24px;
            border: 1px solid rgba(160, 222, 217, 0.3);
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 77, 77, 0.05);
        }

        /* Metric Centering */
        [data-testid="stMetric"] {
            text-align: center !important;
        }
        [data-testid="stMetricValue"] {
            color: #008080;
            justify-content: center !important;
        }
        
        /* Centered Date Header */
        .date-header {
            text-align: center;
            font-size: 1.4rem;
            font-weight: 600;
            color: #004D4D;
            margin-bottom: 25px;
        }

        /* Abstract Blobs in Background */
        [data-testid="stAppViewContainer"]::before, [data-testid="stAppViewContainer"]::after {
            content: "";
            position: fixed;
            z-index: -1;
            filter: blur(80px);
            opacity: 0.5;
        }
        [data-testid="stAppViewContainer"]::before {
            top: -100px; left: -100px; width: 400px; height: 400px;
            background: radial-gradient(circle, rgba(160, 222, 217, 0.4) 0%, transparent 70%);
        }
        [data-testid="stAppViewContainer"]::after {
            bottom: -50px; right: -50px; width: 350px; height: 350px;
            background: radial-gradient(circle, rgba(32, 178, 170, 0.3) 0%, transparent 70%);
        }

        /* Centering content in columns for the navigation cluster */
        [data-testid="column"] > div {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }

        /* TOP NAV ARROWS (Teal Circles, Cream Chevron) */
        div[data-testid="column"]:has(.top-nav-proxy) button {
            background-color: #008080 !important;
            border-radius: 50% !important;
            width: 44px !important;
            height: 44px !important;
            min-width: 44px !important;
            max-width: 44px !important;
            padding: 0 !important;
            border: none !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            box-shadow: 0 4px 12px rgba(0, 77, 77, 0.15) !important;
            transition: all 0.3s ease !important;
        }

        div[data-testid="column"]:has(.top-nav-proxy) button [data-testid="stIconMaterial"] {
            color: #FDFBF7 !important;
            font-size: 1.8rem !important;
            margin: 0 !important;
        }

        div[data-testid="column"]:has(.top-nav-proxy) button:hover {
            background-color: #20B2AA !important;
            transform: scale(1.08) !important;
        }

        /* CALENDAR POPUP (Native Rounded Rect, Teal Border & Icon) */
        div[data-testid="column"]:has(.cal-nav-proxy) button {
            background-color: transparent !important;
            border: 1px solid #008080 !important;
            border-radius: 8px !important;
            box-shadow: none !important;
            height: 44px !important;
            width: auto !important;
            padding: 0 16px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }

        div[data-testid="column"]:has(.cal-nav-proxy) button [data-testid="stIconMaterial"] {
            color: #008080 !important;
            font-size: 1.5rem !important;
            margin: 0 !important;
        }

        div[data-testid="column"]:has(.cal-nav-proxy) button:hover {
            border: 1px solid #20B2AA !important;
            background-color: rgba(0, 128, 128, 0.05) !important;
        }

        /* WEEK SLIDER ARROWS (Transparent, Teal Icon) */
        /* Note: Native streamlit 'tertiary' handles the background transparency already! */
        div[data-testid="column"]:has(.week-nav-proxy) button [data-testid="stIconMaterial"] {
            color: #008080 !important;
            font-size: 2.2rem !important;
        }

        div[data-testid="column"]:has(.week-nav-proxy) button:hover {
            transform: scale(1.15) !important;
        }

        /* FAINT DASHBOARD METRICS INFO BUTTON */
        div[title="Metrics Info"] button p,
        button[title="Metrics Info"] p {
            color: #888 !important;
            font-size: 0.8rem !important;
            font-weight: 400 !important;
            transition: color 0.3s ease;
        }
        
        div[title="Metrics Info"] button:hover p,
        button[title="Metrics Info"]:hover p {
            color: #555 !important;
        }
        </style>
    """, unsafe_allow_html=True)

def card_begin():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

def card_end():
    st.markdown('</div>', unsafe_allow_html=True)
