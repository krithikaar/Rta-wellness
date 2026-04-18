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

        /* FULL-WIDTH TABS */
        div[role="tablist"] {
            width: 100% !important;
            display: flex !important;
            gap: 0px !important;
            padding-bottom: 20px !important;
        }

        div[role="tablist"] button[role="tab"] {
            flex: 1 !important;
            text-align: center !important;
            max-width: none !important;
            border-bottom: 2px solid #e0e4e9 !important;
            padding: 10px 0 !important;
        }
        
        div[role="tablist"] button[aria-selected="true"] {
            background-color: transparent !important;
            border-bottom: 2px solid #008080 !important;
        }

        div[role="tablist"] button[role="tab"] p {
             font-size: 0.95rem !important;
             font-weight: 500 !important;
             color: #004D4D !important;
             margin: 0 !important;
        }

        /* SLIDER THUMB VISIBILITY */
        div[data-testid="stSlider"] [role="slider"],
        div[data-testid="stSelectSlider"] [role="slider"] {
            background-color: #008080 !important;
            border: 2px solid #008080 !important;
            box-shadow: 0 0 2px rgba(0, 0, 0, 0.2) !important;
            height: 18px !important;
            width: 18px !important;
            z-index: 2 !important;
        }
        
        div[data-testid="stSlider"] [role="slider"]:hover,
        div[data-testid="stSelectSlider"] [role="slider"]:hover {
            transform: scale(1.1);
            background-color: #004D4D !important;
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

        /* Center Dashboard Radio Toggle */
        div[data-testid="stSlider"] {
            padding-bottom: 20px !important;
        }
        
        div[data-testid="stSlider"] label {
            color: #008080 !important;
            font-weight: 500 !important;
        }

        /* Styling for the selector handles and tracks */
        div[data-baseweb="slider"] > div > div {
            background: #008080 !important;
        }
        
        div[role="slider"] {
            border-color: #008080 !important;
            background-color: #FDFBF7 !important;
        }

        /* INPUT FIELDS (Restoring the 'shaded box' look) */
        div[data-baseweb="input"], 
        div[data-baseweb="select"], 
        div[data-baseweb="textarea"],
        [data-testid="stNumberInput"] div[data-baseweb="base-input"],
        [data-testid="stTextInput"] div[data-baseweb="base-input"] {
            background-color: #f1f3f6 !important;
            border: 1px solid #e0e4e9 !important;
            border-radius: 10px !important;
            transition: all 0.2s ease !important;
        }

        div[data-baseweb="input"]:focus-within, 
        div[data-baseweb="select"]:focus-within, 
        div[data-baseweb="textarea"]:focus-within {
            border-color: #008080 !important;
            background-color: #ffffff !important;
            box-shadow: 0 0 0 1px #008080 !important;
        }

        input, textarea {
            color: #004D4D !important;
        }
        </style>
    """, unsafe_allow_html=True)

def card_begin():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

def card_end():
    st.markdown('</div>', unsafe_allow_html=True)
