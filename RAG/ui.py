import os
import tempfile
import streamlit as st
from streamlit_chat import message
from RAG_pipe import gen
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

page()