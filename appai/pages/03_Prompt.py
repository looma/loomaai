import os
import sys
import tempfile
import streamlit as st
from streamlit_chat import message
#st.set_option('client.showErrorDetails', False)

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.RAG import *
import tempfile

def filePath(file):
    """
    Takes in a file and creates a temporary file directiory (for streamlit)
    - Returns a file path where the file is stored temporarily 
    """
    with tempfile.NamedTemporaryFile(delete=False) as tf: # tf is temporary file 
        if file is not None:
            tf.write(file.getbuffer()) # Write the file information in tf 
            file_path = tf.name # Assigns file path the temporary file path name 
            return file_path # Returns file path
    
def fileUpload(key):
    """
    Creates a file uploader in streamlit and returns path chosen by user
    - key is a unique associated with the file_uploader within streamlit 
    - checks if user uploaded a file or not, if so it returns the path by calling filePath(file)
    """
    uploaded_file = st.file_uploader('Choose your .pdf file', type="pdf", key=key) # Creates file uploader
    file_path = None
    if filePath(uploaded_file) is not None: # Null check 
        file_path = filePath(uploaded_file) # Gets temporary file path 

    return file_path 


def page():
    """
    Initializes page
    - Depends on choice(), common.RAG
    - Uses file_path recieved from choice() to invoke chain with user query
    """

    st.title("RAG implement")

    file_path = choice() # Creates choice 

    query = st.text_input("User input")

    if file_path is not None:
        model = gen() # Initializes model from RAG.py
        model.makeChain(file_path) # Makes chain 

        response = model.ask(query) # Gets response from chain 

        st.write(response)
    else:
        st.write("No current file")

def textbooks(): 
    """
    Creates dropboxes with all the textbooks generated from split.py
    """
    textbooks_path = os.path.join(os.path.join(os.path.dirname(__file__), '..'), 'textbooks')
    files = os.listdir(textbooks_path) # Files of all textbooks 

    classes = [] # List for classes 

    for file in files: 
        classes.append(file) # Appends all the classes ex: Class1, Class2, etc 

    classSelected = st.selectbox("Class", (classes)) # Creates dropbox for classes

    class_path = os.path.join(os.path.join(os.path.dirname(__file__), '../textbooks/'), classSelected) # Enters directory for class selected
    subjects = os.listdir(class_path) # Lists all files within dir

    subjects_available = [] # List for all subjects avaiable within selected class

    for subject in subjects:
        subjects_available.append(subject) # Appends all the subjects ex: Math, Nepali, etc. 

    subjectSelected = st.selectbox("Subject", (subjects_available)) # Creates dropbox for subjects 

    subject_books_path = os.path.join(os.path.dirname(__file__), '../textbooks/' + classSelected + "/" + subjectSelected + "/textbook_chapters") # Enters directory of subject selected
    subject_books = os.listdir(subject_books_path) # Lists all files within dir

    subject_books_available = [] # List for all books avaiable within subject dir

    for book in subject_books:
        subject_books_available.append(book) # Appends all possible books available 

    book_selected = st.selectbox("Book", (subject_books_available)) # Creates dropbox for book selection

    return os.path.join(os.path.dirname(__file__), '../textbooks/' + classSelected + "/" + subjectSelected + "/textbook_chapters/" + book_selected) # Final file path for selected book

def choice():
    """
    Creates selection which allows user to either upload a file or choose from existing textbooks
    """
    file_path = None 
    choice = st.radio("Choose an option:", ("Upload a file", "Choose existing textbook")) # Creates choice for user

    if choice == "Upload a file":
        uploaded = fileUpload("03_1") 
        file_path = None if uploaded is None else uploaded
    else:
        file_path = textbooks()

    return file_path
    
def main():
    page() # Initlaizes page 


if __name__ == "__main__":
    main() 