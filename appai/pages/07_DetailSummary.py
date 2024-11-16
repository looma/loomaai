import os
import sys
import io
import zipfile
import tempfile
from common.summary import Summary
import streamlit as st
from streamlit_chat import message
from common.config import *
from langchain_openai import ChatOpenAI
from common.summary import *

# Defining the filepath for uploading the file that needs to be summarized
def filePath(file):
    if file is not None:
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            tf.write(file.getbuffer())
            file_path = tf.name
            return file_path
    return None

# Uploading the file into the filepath (allows multiple PDF uploads)
def fileUpload(key):
    uploaded_files = st.file_uploader('Choose your .pdf files', type="pdf", key=key, accept_multiple_files=True)
    file_paths = []
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = filePath(uploaded_file)
            if file_path is not None:
                file_paths.append(file_path)

    return file_paths

# Main streamlit application
def main():
    st.title("Detailed Page Summarizer")
    cfg = ConfigInit()

    # Allow multiple PDF files to be uploaded
    file_paths = fileUpload("04_1")

    # For the summary loading visualization
    if "summary_generated" not in st.session_state:
        st.session_state["summary_generated"] = False

    if file_paths:
        if st.button("Summarize All PDFs"):
            summaries = []
            with st.spinner("Summarizing..."):
                for file_path in file_paths:
                    summarizer = Summary(cfg, file_path)
                    
                    # Extract text from the PDF
                    text_content = summarizer.extract_text_from_pdf()

                    # Generate the summary
                    summary = summarizer.detailSummary_pdf(text_content)
                    summaries.append(summary)
            
            # Display summaries for each PDF
            for i, summary in enumerate(summaries):
                st.write(f"### Summary of File {i+1}")
                st.info(summary)

            # Store the summaries in session state
            st.session_state["content"] = summaries
            st.session_state["summary_generated"] = True
            '''if st.button("Download the summaries", summaries):
                zip_buffer = io.BytesIO()

        # Create a zip file
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for i, summary in enumerate(summaries):
                # Create a text file for each summary
                zip_file.writestr(f"summary_{i + 1}.txt", summary)

        # Set the buffer's position to the beginning
        zip_buffer.seek(0)

        # Provide the zip file for download
        st.download_button(
            label="Download All Summaries as Zip",
            data=zip_buffer,
            file_name="summaries.zip",
            mime="application/zip"
            
        )'''

if __name__ == "__main__":
    main()
