import os
import pathlib
import sys
import time

import pandas as pd
import streamlit as st
from langchain_openai import ChatOpenAI
from pymongo import MongoClient
from streamlit.runtime.state import session_state

from common.config import *
from common.utils import *

from common.generate import generate_vectors

from common.split import split

st.set_page_config(page_title="Split Chapter PDFs", page_icon=os.path.join('images', 'favicon.ico'), layout="wide",
                   menu_items=None)

import streamlit as st
import sys

# Streamlit app code
st.title("Function Output Viewer")

if st.button("Embed Chapters"):
    cfg = ConfigInit()
    openai_api_key = cfg.getv("openai_api_key")
    datadir = cfg.getv("datadir")
    llm = ChatOpenAI(temperature=0, model_name="gpt-4o", api_key=openai_api_key)
    client = MongoClient("mongodb://host.docker.internal:47017/")
    generate_vectors(llm, client, datadir+"/files/chapters")

if st.button("Split Chapters"):
    cfg = ConfigInit()
    datadir = cfg.getv("datadir")
    client = MongoClient("mongodb://host.docker.internal:47017/")
    split(client, datadir+"/files/chapters")