import os

import streamlit as st
import logging

from common.translate_lessons import translate_one_lesson
from common.streamlit_mongo_viewer import mongodb_viewer
from pymongo import MongoClient

from common.llmselect import LLMSelect, LLMInfo

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

    # Add LLM provider/model selection
    providers = LLMInfo().get_providers()
    selected_llm = st.selectbox("Select LLM Provider:", providers, index=0)
    models = LLMInfo().get_model_list(selected_llm)
    selected_model = st.selectbox("Select Model:", models, index=0)
    llm = LLMSelect(selected_llm, selected_model).llm()

    st.markdown("""
    If a lesson has a "translated" field, the lesson will not be translated. 
    Iterates through all lessons in MongoDB, finds inline text elements, 
    and creates a field `data.nepali` which is the translation of `data.html`.
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
