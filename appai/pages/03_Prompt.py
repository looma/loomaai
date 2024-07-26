import os
import sys
import tempfile
import streamlit as st
from streamlit_chat import message

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.RAG import *
import tempfile

def filePath(file):
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tf.write(file.getbuffer())
        file_path = tf.name
        return file_path


def page():

    st.title("RAG implement")

    uploaded_file = st.file_uploader('Choose your .pdf file', type="pdf")    
    st.write(uploaded_file)

    file_path = filePath(uploaded_file)

    query = st.text_input("User input")

    model = gen()
    st.write(file_path)
    model.loadPDF(file_path)

    response = model.ask(query)

    st.write(response)

def dropDown(): 
    st

page()