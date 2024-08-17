import os
import sys
import tempfile
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
    openai_api_key = cfg.getv("openai_api_key")
    llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini", api_key=openai_api_key)

    file = fileUpload("04_1")
    file_path = None if file is None else file
    
    chapter_language = st.radio("Language of PDF: ", options=["Nepali", "English"])
       
    if "summary_generated" not in st.session_state:
        st.session_state["summary_generated"] = False

    if st.button("Summarize"):
        if file_path is not None:
            with st.spinner("Summarizing..."):
                text_content = extract_text_from_pdf(file_path, chapter_language)
                summary = summarize_text(llm, text_content, chapter_language)
                st.session_state["content"] = summary
                st.session_state["summary_generated"] = True
                st.info(summary)
        else:
            st.error("Please upload a PDF file before summarizing.")

    if st.session_state["summary_generated"]:
        if st.button("Translate"):
            if chapter_language == "Nepali":
                tolanguage = "English"
            else:
                tolanguage = "Nepali"
            with st.spinner("Translating..."):
                content = st.session_state["content"]
                translated_content = translate_text(llm, content, tolanguage)
                st.info(translated_content)

        summary = summarize_pdf(file_path, chapter_language, llm)
        st.write(summary)

if __name__ == "__main__":
    main()