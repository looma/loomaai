import streamlit as st
from pymongo import MongoClient
from common.split import *
from common.config import ConfigInit

from common.streamlit_mongo_viewer import mongodb_viewer

def TextbookUI(cfg):
    config = cfg.json()
    st.title('Textbook')
    split_text, remove, dict, embed = st.tabs(['Split Textbook', 'Remove Textbook', 'Dictionary', 'Embed'])

    with split_text:
        MONGO_URI=f'mongodb://{config["mongo"]["host"]}:{config["mongo"]["port"]}/dashboard'
        DATABASE_NAME = f'{config["mongo"]["database"]}'
        FILTERS = {}
        selected = mongodb_viewer(
            client_uri=MONGO_URI,
            database_name=DATABASE_NAME,
            collection_name="textbooks",
            filters=FILTERS,
            columns=["prefix", "dn"]
        )

        textbooks = [t['prefix'] for t in selected]
        if st.button("Split Chapters"):
            with st.spinner("Splitting..."):
                #gets the directory that the chapters have to go to
                datadir = config["datadir"]
                #calls the MongoClient and runs the split function in loomaai/appai/common/split.py
                client = MongoClient(MONGO_URI)
                split(client, datadir, textbooks[0]) # TODO: make this accept multiple prefixes

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
