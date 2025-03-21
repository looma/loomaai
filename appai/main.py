import os

import streamlit as st

st.title("LoomaAI")

try:
    print("loomaai initialized")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    datadir = os.getenv("DATADIR")
    print("datadir: " + datadir)
except Exception as e:
    st.error(str(e))
