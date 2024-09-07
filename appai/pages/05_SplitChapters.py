import streamlit as st
from langchain_openai import ChatOpenAI
from pymongo import MongoClient

from common.config import *
from common.utils import *

from common.generate import generate_vectors

from common.split import split

st.set_page_config(page_title="Split Chapter PDFs", page_icon=os.path.join('images', 'favicon.ico'), layout="wide",
                   menu_items=None)

import streamlit as st
st.title("Split Chapter PDFs")

if st.button("Embed Chapters"):
    cfg = ConfigInit()
    openai_api_key = cfg.getv("openai_api_key")
    datadir = cfg.getv("datadir")
    llm = ChatOpenAI(temperature=0, model_name="gpt-4o", api_key=openai_api_key)
    client = MongoClient("mongodb://host.docker.internal:47017/")
    generate_vectors(llm, client, datadir+"/files/chapters", lambda chapter: st.write("Processed" + chapter))