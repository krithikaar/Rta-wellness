import streamlit as st

st.markdown("### Top Nav Row")
st.columns([1, 4, 1, 4, 1])[0].button("", icon=":material/chevron_left:", key="nav_l")

st.markdown('<div id="week-nav-trigger"></div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 10, 1])
col1.button("", icon=":material/chevron_left:", key="w_prev")
col3.button("", icon=":material/chevron_right:", key="w_next")

st.markdown("""
<style>
/* General Style */
div[data-testid="stButton"] button {
    border-radius: 50% !important;
    width: 44px !important;
    height: 44px !important;
    background-color: teal !important;
}

/* Specific Targeting */
/* Target the row immediately following the div containing our marker */
div:has(> div[data-testid="stMarkdownContainer"] > div#week-nav-trigger) + div[data-testid="stHorizontalBlock"] button {
    background-color: #FDFBF7 !important;
    border: 2px solid #008080 !important;
}

div:has(> div[data-testid="stMarkdownContainer"] > div#week-nav-trigger) + div[data-testid="stHorizontalBlock"] button [data-testid="stIconMaterial"] {
    color: #008080 !important;
}
</style>
""", unsafe_allow_html=True)
