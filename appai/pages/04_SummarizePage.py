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
    llm = ChatOpenAI(temperature=0, model_name="gpt-4o", api_key=openai_api_key)

    file = fileUpload("04_1")
    file_path = None if file is None else file

    pages = extract_text(file_path)
    st.write(pages)
    summary = query_llm(llm, pages, 50)

    st.write(summary)

if __name__ == "__main__":
    main()