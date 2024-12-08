import streamlit as st

from common.query import query
from common.config import *

from langchain_huggingface import HuggingFaceEmbeddings
from pymongo import MongoClient
from qdrant_client import QdrantClient
from logzero import logging



def SearchUI(cfg):
    config = cfg.json()
    st.title("Looma Content Search")
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

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Search Message ..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            results = query(prompt, qclient)
            st.json([e for e in results])
            # for e in results:
            # pdf_viewer(cfg.getv('datadir') + "/" + e.dict()["metadata"]["source"])

if __name__ == "__main__":
    try:
        cfg = ConfigInit()
        SearchUI(cfg)
    except Exception as e:
        st.error(str(e))
        logging.error(str(e))
        st.stop()
