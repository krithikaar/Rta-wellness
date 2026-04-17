import streamlit as st

st.button("LEFT", icon=":material/chevron_left:", key="test_l")
st.button("RIGHT", icon=":material/chevron_right:", key="test_r")

st.markdown("""
<style>
/* Try to target by text using a trick? No. */
/* Target by icon? */
div[data-testid="stButton"] button:has(svg) {
    background-color: red !important;
}
</style>
""", unsafe_allow_html=True)
