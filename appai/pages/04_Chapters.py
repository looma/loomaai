import os
import sys
import io
import zipfile
import tempfile
from common.summary import Summary
import streamlit as st
from common.config import *
from langchain_openai import ChatOpenAI
from common.summary import *
from common.config import ConfigInit
from common.streamlit_mongo_viewer import mongodb_viewer
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

def ChaptersUI(cfg):
    st.title("Chapters")
    MONGO_URI = "mongodb://host.docker.internal:47017"
    DATABASE_NAME = "looma"

    with st.expander("Select Textbooks", expanded=True):
        selected_textbooks = mongodb_viewer(
            client_uri=MONGO_URI,
            database_name=DATABASE_NAME,
            collection_name="textbooks",
            filters={},
            columns=["_id", "dn", "prefix"]
        )

    if len(selected_textbooks) > 0:
        with st.expander("Select Chapters", expanded=True):
            prefixes = [textbook["prefix"] for textbook in selected_textbooks]
            selected_chapters = mongodb_viewer(
                client_uri=MONGO_URI,
                database_name=DATABASE_NAME,
                collection_name="chapters",
                filters={
                    "_id": {"$regex": "^(" + "|".join(prefixes) + ")"}
                },
                columns=["_id", "dn"]
            )
            st.json(selected_chapters)

    # TODO: get the file names for the selected chapters

    summary1, supersummary1, translate1, topic1, quiz1 = st.tabs(["Summary", "Detailed Summary", "Translate", "Topic", "Quiz"])

    with quiz1:
        file_paths = fileUpload("04_1")

        # For the quiz loading visualization
        if "quizzes_generated" not in st.session_state:
            st.session_state["quizzes_generated"] = False

        if file_paths:
            if st.button("Quizzes for all PDFs"):
                quizzes = []
                with st.spinner("Generating..."):
                    for file_path in file_paths:
                        quizzer = Summary(cfg, file_path)
                        
                        # Generate the summary
                        quiz = quizzer.quiz_pdf()
                        quizzes.append(quiz)
                
                # Display summaries for each PDF
                for i, quiz in enumerate(quizzes):
                    st.write(f"### Quiz of File {i+1}")
                    st.info(quiz)

                # Store the summaries in session state
                st.session_state["content"] = quizzes
                st.session_state["quizzes_generated"] = True
    with supersummary1:
        file_paths = fileUpload("04_2")

        # For the summary loading visualization
        if "summary_generated" not in st.session_state:
            st.session_state["summary_generated"] = False

        if file_paths:
            if st.button("Summarize All PDFs", key="supersummaries_button"):
                summaries = []
                with st.spinner("Summarizing..."):
                    for file_path in file_paths:
                        summarizer = Summary(cfg, file_path)

                        # Generate the summary
                        summary = summarizer.detailSummary_pdf()
                        summaries.append(summary)
                
                # Display summaries for each PDF
                for i, summary in enumerate(summaries):
                    st.write(f"### Summary of File {i+1}")
                    st.info(summary)

                # Store the summaries in session state
                st.session_state["content"] = summaries
                st.session_state["summary_generated"] = True
                
    with translate1:
        file_paths = fileUpload("04_3")

        # For the quiz loading visualization
        if "quizzes_generated" not in st.session_state:
            st.session_state["quizzes_generated"] = False

        if file_paths:
            if st.button("Translations for all PDFs", key="quizzes_button"):
                translations = []
                with st.spinner("Generating..."):
                    for file_path in file_paths:
                        translater = Summary(cfg, file_path)
                        
                        # Generate the summary
                        translate = translater.translate_pdf()
                        translations.append(translate)
                
                # Display summaries for each PDF
                for i, translate in enumerate(translations):
                    st.write(f"### Translation of File {i+1}")
                    st.info(translate)

                # Store the summaries in session state
                st.session_state["content"] = translations
                st.session_state["quizzes_generated"] = True
                
    with topic1:
        file_paths = fileUpload("04_4")

        # For the summary loading visualization
        if "summary_generated" not in st.session_state:
            st.session_state["summary_generated"] = False

        if file_paths:
            if st.button("Chapter Topics", key="Chapter_button"):
                topics = []
                with st.spinner("Analysing..."):
                    for file_path in file_paths:
                        topicizer = Summary(cfg, file_path)
                        
                        # Generate the summary
                        topic = topicizer.topic_pdf()
                        topics.append(topic)
                    # Display summaries for each PDF
                    for i, topic in enumerate(topics):
                        st.write(f"### Topics of File {i+1}")
                        st.info(topic)
                

                # Store the summaries in session state
                st.session_state["content"] = topics
                st.session_state["summary_generated"] = True
                
    with summary1:
        file_paths = fileUpload("04_5")

        # For the summary loading visualization
        if "summary_generated" not in st.session_state:
            st.session_state["summary_generated"] = False

        if file_paths:
            if st.button("Summarize All PDFs", key="summarize_button"):
                summaries = []
                with st.spinner("Summarizing..."):
                    for file_path in file_paths:
                        summarizer = Summary(cfg, file_path)
                        
                        # Generate the summary
                        summary = summarizer.summarize_pdf()
                        summaries.append(summary)
                    # Display summaries for each PDF
                    for i, summary in enumerate(summaries):
                        st.write(f"### Summary of File {i+1}")
                        st.info(summary)
                

                # Store the summaries in session state
                st.session_state["content"] = summaries
                st.session_state["summary_generated"] = True
                
if __name__ == '__main__':
    try:
        cfg = ConfigInit()
        ChaptersUI(cfg)
    except Exception as e:
        st.error(str(e))
