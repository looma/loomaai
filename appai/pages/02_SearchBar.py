import streamlit as st

from appai.common.query_faiss import query
from streamlit_pdf_viewer import pdf_viewer

from common.config import *
# from common.files import *
# from common.utils import *

st.title("Looma Content Search")

cfg = ConfigInit()
data_dir = cfg.getv("datadir")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Search Message ..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        results = query(prompt, data_dir)
        st.json([e.dict()["metadata"] for e in results])
        for e in results:
            pdf_viewer(data_dir + "/files/chapters/" + e.dict()["metadata"]["source"])
