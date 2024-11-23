import streamlit as st
from pymongo import MongoClient
from common.split import *

from common.config import ConfigInit

def TextbookUI(cfg):
    st.title('Textbook')
    split_text, remove, dict, embed = st.tabs(['Split Textbook', 'Remove Textbook', 'Dictionary', 'Embed'])
    
    with split_text:
        textbooks = st.text_input("What textbooks need to be split. Type 'all' for all the textbooks or the textbook prefix for a specific textbook")

        if st.button("Split Chapters"):
            with st.spinner("Splitting..."):
                #gets the directory that the chapters have to go to  
                cfg = ConfigInit()
                datadir = cfg.getv("datadir")
                
                #calls the MongoClient and runs the split function in loomaai/appai/common/split.py
                client = MongoClient("mongodb://host.docker.internal:47017/")
                split(client, datadir, textbooks)
                
                st.write("all textbook chapters have their own pdfs")
                
    with remove:
        st.write('hi')
        
    with dict:
        st.write('hi')

    with embed:
        st.write('hi')


if __name__ == '__main__':
    try:
        cfg = ConfigInit()
        TextbookUI(cfg)
    except Exception as e:
        st.error(str(e))
    
