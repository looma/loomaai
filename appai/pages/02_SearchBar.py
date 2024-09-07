import streamlit as st

from streamlit_pdf_viewer import pdf_viewer

from common.query import query
from common.config import *

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from pymongo import MongoClient
from qdrant_client import QdrantClient

st.title("Looma Content Search")

client = MongoClient("mongodb://host.docker.internal:47017/")
model_name = "sentence-transformers/all-mpnet-base-v2"
model_kwargs = {}
encode_kwargs = {'normalize_embeddings': False}
hf = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)
qclient = QdrantClient(url='http://qdrant:6333')

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Search Message ..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    cfg = ConfigInit()
    with st.chat_message("user"):
        results = query(prompt, qclient)
        st.json([e for e in results])
        # for e in results:
        # pdf_viewer(cfg.getv('datadir') + "/" + e.dict()["metadata"]["source"])
