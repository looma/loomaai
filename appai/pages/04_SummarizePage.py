import tempfile
import streamlit as st
from common.config import *
from common.summary import *

#defining the filepath for uploading the file that needs to be summarized
def filePath(file):
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        if file is not None:
            tf.write(file.getbuffer())
            file_path = tf.name
            return file_path
        
#uploading the file into the filepath
def fileUpload(key):
    uploaded_file = st.file_uploader('Choose your .pdf file', type="pdf", key=key)    
    file_path = None
    if filePath(uploaded_file) is not None:
        file_path = filePath(uploaded_file)

    return file_path

#main streamlit application
def main():
    st.title("Page Summarizer")
    cfg = ConfigInit()

    file = fileUpload("04_1")
    file_path = None if file is None else file
    
    chapter_language = st.radio("Language of PDF: ", options=["Nepali", "English"])

    #for the summary loading visualization   
    if "summary_generated" not in st.session_state:
        st.session_state["summary_generated"] = False

    if file_path:
        summarizer = Summary(cfg, file_path)

#calling summary from common and summarizing the text from the PDF into streamlit
        if st.button("Summarize"):
            with st.spinner("Summarizing..."):
                text_content = summarizer.extract_text()
                summary = summarizer.summarize_text(text_content, chapter_language)
                st.session_state["content"] = summary
                st.session_state["summary_generated"] = True
                st.info(summary)
                
#calling summary from common and translating the text from the summary        
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