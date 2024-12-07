import streamlit as st
from common.split import *
from common.config import ConfigInit

from common.streamlit_mongo_viewer import mongodb_viewer

if __name__ == "__main__":
    st.title('Textbook')
    split_text, remove, dict, embed = st.tabs(['Split Textbook', 'Remove Textbook', 'Dictionary', 'Embed'])

    with split_text:
        MONGO_URI = "mongodb://host.docker.internal:47017"
        DATABASE_NAME = "looma"

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

                cfg = ConfigInit()
                datadir = cfg.getv("datadir")

                #calls the MongoClient and runs the split function in loomaai/appai/common/split.py
                client = MongoClient("mongodb://host.docker.internal:47017/")
                split(client, datadir, textbooks[0]) # TODO: make this accept multiple prefixes

                st.write("all textbook chapters have their own pdfs")

    with remove:
        st.write('hi')

    with dict:
        st.write('hi')

    with embed:
        st.write('hi')