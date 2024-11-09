import streamlit as st
from langchain_openai import ChatOpenAI
from pymongo import MongoClient

from common.config import *
from common.utils import *

from common.split import split

st.set_page_config(page_title="Split Chapter PDFs", page_icon=os.path.join('images', 'favicon.ico'), layout="wide",
                   menu_items=None)

import streamlit as st
st.title("Split Chapter PDFs")

#textbox that determines what chapters need to be split
textbooks = st.text_input("What textbooks need to be split. Type 'all' for all the textbooks or the textbook prefix for a specific chapter")

if st.button("Split Chapters"):
    #gets the directory that the chapters have to go to from 
    cfg = ConfigInit()
    datadir = cfg.getv("datadir")
    
    #calls the MongoClient and runs the split function in loomaai/appai/common/split.py
    client = MongoClient("mongodb://host.docker.internal:47017/")
    split(client, datadir+"/files/chapters", textbooks)
    st.write("all textbook chapters have their own pdfs")