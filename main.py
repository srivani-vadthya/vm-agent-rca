import streamlit as st

st.set_page_config(page_title="RCA Analyst", layout="wide", page_icon="🔎")

st.markdown("""
<style>
* { font-family: 'Inter', sans-serif; }
.stApp { background: #f4f6f9; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { max-width: 900px; padding-top: 4rem; }
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border-color: #dde3ea;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;padding:1rem 2rem 2.5rem 2rem;">
    <h1 style="font-size:2.5rem;color:#1a2332;margin-bottom:1rem;">RCA Analyst</h1>
    <p style="font-size:1.1rem;color:#6b7c93;margin-bottom:0;">AI-powered root cause analysis platform</p>
</div>
""", unsafe_allow_html=True)

left, right = st.columns(2, gap="large")

with left:
    with st.container(border=True):
        st.markdown("### User Chat")
        st.caption("Ask questions and analyze logs.")
        st.page_link("pages/💬_chat_interface.py", label="Open User Chat")

with right:
    with st.container(border=True):
        st.markdown("### Admin Panel")
        st.caption("Manage the knowledge base.")
        st.page_link("pages/📊_admin_panel.py", label="Open Admin Panel")
