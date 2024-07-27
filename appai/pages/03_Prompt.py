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


def page():

    st.title("RAG implement")

    file_path = choice()

    query = st.text_input("User input")

    if file_path is not None:
        model = gen()
        st.write(file_path)
        model.loadPDF(file_path)

        response = model.ask(query)

        st.write(response)
    else:
        st.write("No current file")

def textbooks(): 
    textbooks_path = os.path.join(os.path.join(os.path.dirname(__file__), '..'), 'textbooks')
    files = os.listdir(textbooks_path)

    classes = []

    for file in files:
        classes.append(file)

    classSelected = st.selectbox("Class", (classes))

    class_path = os.path.join(os.path.join(os.path.dirname(__file__), '../textbooks/'), classSelected)
    subjects = os.listdir(class_path)

    subjects_available = []

    for subject in subjects:
        subjects_available.append(subject)

    subjectSelected = st.selectbox("Subject", (subjects_available))

    subject_books_path = os.path.join(os.path.dirname(__file__), '../textbooks/' + classSelected + "/" + subjectSelected + "/textbook_chapters")
    subject_books = os.listdir(subject_books_path)

    subject_books_available = []

    for book in subject_books:
        subject_books_available.append(book)

    book_selected = st.selectbox("Book", (subject_books_available))

    return os.path.join(os.path.dirname(__file__), '../textbooks/' + classSelected + "/" + subjectSelected + "/textbook_chapters/" + book_selected)

def choice():
    file_path = None 
    choice = st.radio("Choose an option:", ("Upload a file", "Choose existing textbook"))

    if choice == "Upload a file":
        file_path = None if fileUpload() is None else fileUpload()
    else:
        file_path = textbooks()

    return file_path
    
def main():
    page()


if __name__ == "__main__":
    main()