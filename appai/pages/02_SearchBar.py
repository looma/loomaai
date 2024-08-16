import streamlit as st

from streamlit_pdf_viewer import pdf_viewer

from common.query_faiss import query
from common.config import *

st.title("Looma Content Search")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Search Message ..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    cfg = ConfigInit()
    with st.chat_message("user"):
        results = query(prompt, cfg.getv('datadir'))
        st.json([e.dict()["metadata"] for e in results])
        for e in results:
            pdf_viewer(cfg.getv('datadir') + "/" + e.dict()["metadata"]["source"])
