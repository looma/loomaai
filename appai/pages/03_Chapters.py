import os
import tempfile
import streamlit as st

from common.activity_chapter import chapter_url_from_id
from common.summary import *
from common.embed import objectid_to_uuid
from common.populate_relevant_resources import populate_resources_for_chapter
from common.config import ConfigInit
from common.streamlit_mongo_viewer import mongodb_viewer
from pymongo import MongoClient
from qdrant_client import QdrantClient

from common.dict import Dictionary


# Defining the filepath for uploading the file that needs to be summarized
def filePath(file):
    if file is not None:
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            tf.write(file.getbuffer())
            file_path = tf.name
            return file_path
    return None


def ChaptersUI(cfg):
    config = cfg.json()
    st.title("Chapters")
    MONGO_URI = f"mongodb://{config['mongo']['host']}:{config['mongo']['port']}"
    DATABASE_NAME = f"{config['mongo']['database']}"
    files_dir = config["datadir"]

    qd = QdrantClient(url=f"http://{config['qdrant']['host']}:{config['qdrant']['port']}")

    selected_chapters = []

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

    client = MongoClient(MONGO_URI)
    db = client['looma']

    populate_tab, summary_tab, quiz_tab, dictionary_tab = st.tabs(
        ["Populate Relevant Activities", "Summary", "Quiz", "Dictionary"])  # TODO: add more prompt types

    with populate_tab:
        if len(selected_chapters) > 0:
            st.info("Make sure to embed all activities first (sidebar -> Activities)")
            if st.button("Populate Relevant Activities", key="populate_button"):
                with st.spinner("Populating..."):
                    mongo_activies = list(
                        db.activities.find({"ID": {"$in": [chapter["_id"] for chapter in selected_chapters]}}))
                    qd_chapters = qd.retrieve(collection_name="activities",
                                              ids=[objectid_to_uuid(str(activity["_id"])) for activity in
                                                   mongo_activies], with_vectors=True, with_payload=True)
                    for qd_chapter in qd_chapters:
                        populate_resources_for_chapter(qd, db, qd_chapter)
                st.success("Populated relevant activities in MongoDB for selected chapters")
    with summary_tab:
        if len(selected_chapters) > 0:
            if st.button("Summarize Selection", key="summarize_button"):
                summaries = []
                with st.spinner("Summarizing..."):
                    for chapter in selected_chapters:
                        _, file_path, textbook = chapter_url_from_id(chapter["_id"], files_dir=files_dir, textbook=None, mongo=db)

                        summarizer = Summary(cfg, file_path)
                        summary = summarizer.summarize_pdf()

                        files_dir = config["datadir"]
                        save_loc = f'{files_dir}/{textbook["fp"]}{'en'}'
                        os.makedirs(save_loc, exist_ok=True)
                        save_name = f"{chapter['_id']}.summary"
                        save_info = os.path.join(save_loc, save_name)
                        with open(save_info, "w") as file:
                            file.write(summary)

                        summaries.append(summary)

                # Display summaries for each PDF
                for i, summary in enumerate(summaries):
                    st.write(f"### Summary of File {i + 1}")
                    st.info(summary)
    with quiz_tab:
        if len(selected_chapters) > 0:
            if st.button("Generate Quizzes for Selection"):
                quizzes = []
                with st.spinner("Generating..."):
                    for chapter in selected_chapters:
                        _, file_path, textbook = chapter_url_from_id(chapter["_id"], files_dir=files_dir,  textbook=None, mongo=db)
                        quizzer = Summary(cfg, file_path)

                        # Generate the summary
                        quiz = quizzer.quiz_pdf()
                        save_loc = f'{files_dir}/{textbook["fp"]}{'en'}'
                        os.makedirs(save_loc, exist_ok=True)
                        save_name = f"{chapter['_id']}.quiz"
                        save_info = os.path.join(save_loc, save_name)
                        # Open the file in write mode and write the content
                        with open(save_info, "w") as file:
                            file.write(quiz)
                        quizzes.append(quiz)
                for i, quiz in enumerate(quizzes):
                    st.write(f"### Quiz of File {i + 1}")
                    st.info(quiz)
    with dictionary_tab:
        if len(selected_chapters) > 0:
            if st.button("Update Dictionary with Selection"):
                with st.spinner("Updating..."):
                    for chapter in selected_chapters:
                        _, file_path, textbook = chapter_url_from_id(chapter["_id"], files_dir=files_dir,  textbook=None, mongo=db)
                        quizzer = Summary(cfg, file_path)
                        dictionary_maker = Dictionary(cfg)
                        dictionary_maker.dict_update(chapter["_id"], quizzer.extract_text(), client)
                st.success("Updated dictionary in MongoDB for selected chapters")


if __name__ == '__main__':
    try:
        cfg = ConfigInit()
        ChaptersUI(cfg)
    except Exception as e:
        st.error(str(e))
