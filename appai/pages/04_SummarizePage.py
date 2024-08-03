import os
import sys
import tempfile
import streamlit as st
from streamlit_chat import message

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.summary import *
import tempfile

def filePath(file):
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        if file is not None:
            tf.write(file.getbuffer())
            file_path = tf.name
            return file_path

def fileUpload():
    uploaded_file = st.file_uploader('Choose your .pdf file', type="pdf")    
    file_path = None
    if filePath(uploaded_file) is not None:
        file_path = filePath(uploaded_file)

    return file_path

def main():
    st.title("Page Summarizer")

    fileUpload()

if __name__ == "__main__":
    main()