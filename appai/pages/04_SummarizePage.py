import os
import sys
import tempfile
from common.summary import Summary
import streamlit as st
from streamlit_chat import message
from common.config import *
from langchain_openai import ChatOpenAI
from common.summary import *

def filePath(file):
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        if file is not None:
            tf.write(file.getbuffer())
            file_path = tf.name
            return file_path

def fileUpload(key):
    uploaded_file = st.file_uploader('Choose your .pdf file', type="pdf", key=key)    
    file_path = None
    if filePath(uploaded_file) is not None:
        file_path = filePath(uploaded_file)

    return file_path

def main():
    st.title("Page Summarizer")
    cfg = ConfigInit()

    file = fileUpload("04_1")
    file_path = None if file is None else file
    
    chapter_language = st.radio("Language of PDF: ", options=["Nepali", "English"])
       
    if "summary_generated" not in st.session_state:
        st.session_state["summary_generated"] = False

    if file_path:
        summarizer = Summary(cfg, file_path)

        if st.button("Summarize"):
            with st.spinner("Summarizing..."):
                text_content = summarizer.extract_text_from_pdf(chapter_language)
                summary = summarizer.summarize_text(text_content, chapter_language)
                st.session_state["content"] = summary
                st.session_state["summary_generated"] = True
                st.info(summary)
        
        if st.session_state["summary_generated"]:
            if st.button("Translate"):
                if chapter_language == "Nepali":
                    tolanguage = "English"
                else:
                    tolanguage = "Nepali"
                with st.spinner("Translating..."):
                    content = st.session_state["content"]
                    translated_content = summarizer.translate_text(content, tolanguage)
                    st.info(translated_content)

if __name__ == "__main__":
    main()