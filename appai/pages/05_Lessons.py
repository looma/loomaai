import os

import streamlit as st
import logging

from common.translate_lessons import translate_one_lesson
from common.streamlit_mongo_viewer import mongodb_viewer
from pymongo import MongoClient

from common.llmselect import LLMSelect
# Qdrant server configuration

COLLECTION_NAME = "lessons"


# Streamlit App
def main():
    st.title("Lessons")

    MONGO_URI = os.getenv("MONGO_URI")
    DATABASE_NAME = os.getenv("MONGO_DB")
    FILTERS = {"data": {"$ne": None}}
    selected = mongodb_viewer(
        client_uri=MONGO_URI,
        database_name=DATABASE_NAME,
        collection_name="lessons",
        filters=FILTERS,
        columns=["dn", "ndn", "translator", "translated", "data"],
        hidden_columns=["data"],
    )
    llm = LLMSelect().llm()

    # (translate_tab) = st.tabs(['Translate'])

    # with translate_tab:
    st.markdown("""
    If a lesson is already translated, the existing translation will be overwritten. Iterates through all lessons in MongoDB and creates a field `nepali` which is the translation of `data`.
    """)
    if st.button("Translate"):
        try:
            with st.spinner("Translating..."):
                client = MongoClient(MONGO_URI)
                for lesson in selected:
                    translate_one_lesson(
                        client.get_database(DATABASE_NAME), lesson, llm
                    )
            st.success(f"Translated {len(selected)} lessons")
        except Exception as exception:
            st.error(f"Error in translation: {exception}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(str(e))
        logging.error(str(e))
        st.stop()
