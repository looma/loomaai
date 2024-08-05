import os
import sys

import streamlit as st

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from streamlit_pdf_viewer import pdf_viewer

from common.query_faiss import query
from common.config import *
# from common.files import *
# from common.utils import *

st.title("Looma Content Search")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Search Message ..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        results = query(prompt)
        st.json([e.dict()["metadata"] for e in results])
        for e in results:
            cfg = ConfigInit()
            if 'datadir' not in st.session_state:
                st.session_state['datadir'] = cfg.getv("datadir")
            pdf_viewer(st.session_state['datadir'] + "/" + e.dict()["metadata"]["source"])
