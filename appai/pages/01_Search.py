import streamlit as st

from common.query import query
from common.config import *

from langchain_huggingface import HuggingFaceEmbeddings
from pymongo import MongoClient
from qdrant_client import QdrantClient
from logzero import logging



def SearchUI(cfg):
    config = cfg.json()
    MONGO_URI = f"mongodb://{config['mongo']['host']}:{config['mongo']['port']}"
    client = MongoClient(MONGO_URI)
    
    model_name = "sentence-transformers/all-mpnet-base-v2"
    model_kwargs = {}
    encode_kwargs = {'normalize_embeddings': False}
    hf = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    
    qclient = QdrantClient(url=f'http://{config["qdrant"]["host"]}:{config["qdrant"]["port"]}')
   
    if 'search_text' not in st.session_state:
        st.session_state.search_text = ""
    instr = ""
    with st.form("search_form"):
        col1, col2 = st.columns([7,1])
        with col1:
            query = st.text_input(
                        instr,
                        value=instr,
                        placeholder="Search",
                        label_visibility="collapsed"
            )

            if query != st.session_state.search_text:
                st.session_state.search_text = query
    with col2:
            submitted = st.form_submit_button("Search")

    if query and submitted:
        st.write("Searching...", query)

if __name__ == "__main__":
    try:
        cfg = ConfigInit()
        SearchUI(cfg)
    except Exception as e:
        st.error(str(e))
        logging.error(str(e))
        st.stop()
