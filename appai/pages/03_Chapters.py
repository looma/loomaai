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
                    "_id": {"$regex": "^(" + "|".join(prefixes) + ")(?![A-Z])"},
                    "$or": [{"len": {"$gt": 0}}, {"nlen": {"$gt": 0}}]},
                columns=["_id", "dn"]
            )

    client = MongoClient(MONGO_URI)
    db = client['looma']

    if len(selected_chapters) > 0:

        #add this code to sort selected_chapters by grade level
        import re
        pattern = r"(^\d{1,2}).*"
        replacement = r"\1"
        selected_chapters.sort(key = lambda x: int(re.sub(pattern, replacement, x['_id'])))

        #the sub-order of subjects inside a grade level doesnt matter to our code

        populate_tab, summary_tab, quiz_tab, custom_tab, dictionary_tab = st.tabs(
            ["Populate Relevant Activities", "Summary", "Quiz", "Custom Prompt",
             "Dictionary"])  # TODO: add more prompt types
        with populate_tab:
            st.info("Make sure to embed all activities first (sidebar -> Activities)")
            if st.button("Populate Relevant Activities", key="populate_button"):
                with st.spinner("Populating..."):
                    mongo_activies = list(
                        db.activities.find({"ID": {"$in": [chapter["_id"] for chapter in selected_chapters]}}))
                    print([objectid_to_uuid(str(activity["_id"])) for activity in
                           mongo_activies])
                    qd_chapters = qd.retrieve(collection_name="activities",
                                              ids=[objectid_to_uuid(str(activity["_id"])) for activity in
                                                   mongo_activies], with_vectors=True, with_payload=True)
                    print(qd_chapters)
                    for qd_chapter in qd_chapters:
                        populate_resources_for_chapter(qd, db, qd_chapter)
                    st.success("Populated relevant activities in MongoDB for selected chapters")
        with summary_tab:
            if st.button("Summarize Selection", key="summarize_button"):
                with st.spinner("Summarizing..."):
                    for chapter in selected_chapters:
                        _, file_path_en, _, file_path_np, textbook = chapter_url_from_id(chapter["_id"],
                                                                                         files_dir=files_dir,
                                                                                         textbook=None, mongo=db)

                        summarizer = Summary(cfg, file_path_en, file_path_np,
                                             "Please summarize the following text in one paragraph in the same language it is written in \n if the text is in Nepali keep it in Nepali and if the text is in English keep it in English\n{text}")
                        summary_en, summary_np = summarizer.prompt_pdf()

                        if summary_en is not None:
                            files_dir = config["datadir"]
                            save_loc = f'{files_dir}/{textbook["fp"]}{'en'}'
                            os.makedirs(save_loc, exist_ok=True)
                            save_name = f"{chapter['_id']}.summary"
                            save_info = os.path.join(save_loc, save_name)
                            with open(save_info, "w") as file:
                                file.write(summary_en)

                        if summary_np is not None:
                            files_dir = config["datadir"]
                            save_loc = f'{files_dir}/{textbook["fp"]}{'np'}'
                            os.makedirs(save_loc, exist_ok=True)
                            save_name = f"{chapter['_id']}-np.summary"
                            save_info = os.path.join(save_loc, save_name)
                            with open(save_info, "w") as file:
                                file.write(summary_np)

                        st.info(f"{summary_en} \n \n {summary_np}")
        with quiz_tab:
            if st.button("Generate Quizzes for Selection"):
                with st.spinner("Summarizing..."):
                    for chapter in selected_chapters:
                        _, file_path_en, _, file_path_np, textbook = chapter_url_from_id(chapter["_id"],
                                                                                         files_dir=files_dir,
                                                                                         textbook=None, mongo=db)

                        summarizer = Summary(cfg, file_path_en, file_path_np,
                                             "Please make a quiz of the following text in the same language it is written in. Make an answer key but make sure answers are not shown at all on the quiz itself. If the text is in Nepali keep it in Nepali and if the text is in English keep it in English \n {text}")
                        summary_en, summary_np = summarizer.prompt_pdf()

                        if summary_en is not None:
                            files_dir = config["datadir"]
                            save_loc = f'{files_dir}/{textbook["fp"]}{'en'}'
                            os.makedirs(save_loc, exist_ok=True)
                            save_name = f"{chapter['_id']}.quiz"
                            save_info = os.path.join(save_loc, save_name)
                            with open(save_info, "w") as file:
                                file.write(summary_en)

                        if summary_np is not None:
                            files_dir = config["datadir"]
                            save_loc = f'{files_dir}/{textbook["fp"]}{'np'}'
                            os.makedirs(save_loc, exist_ok=True)
                            save_name = f"{chapter['_id']}-np.quiz"
                            save_info = os.path.join(save_loc, save_name)
                            with open(save_info, "w") as file:
                                file.write(summary_np)

                        st.info(f"{summary_en} \n \n {summary_np}")
        with custom_tab:
            prompt = st.text_input("Prompt text", "")
            extension = st.text_input("File extension", "")
            if st.button("Generate"):
                with st.spinner("Summarizing..."):
                    for chapter in selected_chapters:
                        _, file_path_en, _, file_path_np, textbook = chapter_url_from_id(chapter["_id"],
                                                                                         files_dir=files_dir,
                                                                                         textbook=None, mongo=db)

                        summarizer = Summary(cfg, file_path_en, file_path_np, prompt + "\n \n {text}")
                        summary_en, summary_np = summarizer.prompt_pdf()

                        if summary_en is not None:
                            files_dir = config["datadir"]
                            save_loc = f'{files_dir}/{textbook["fp"]}{'en'}'
                            os.makedirs(save_loc, exist_ok=True)
                            save_name = f"{chapter['_id']}.{extension}"
                            save_info = os.path.join(save_loc, save_name)
                            with open(save_info, "w") as file:
                                file.write(summary_en)

                        if summary_np is not None:
                            files_dir = config["datadir"]
                            save_loc = f'{files_dir}/{textbook["fp"]}{'np'}'
                            os.makedirs(save_loc, exist_ok=True)
                            save_name = f"{chapter['_id']}-np.{extension}"
                            save_info = os.path.join(save_loc, save_name)
                            with open(save_info, "w") as file:
                                file.write(summary_np)

                        st.info(f"{summary_en} \n \n {summary_np}")
        with dictionary_tab:
            if st.button("Update Dictionary with Selection"):
                with st.spinner("Updating..."):
                    for chapter in selected_chapters:
                        _, file_path, _, nepali_fp, textbook = chapter_url_from_id(chapter["_id"], files_dir=files_dir, textbook=None, mongo=db)
                        quizzer = Summary(cfg, file_path, nepali_fp, "")
                        dictionary_maker = Dictionary(cfg)
                        text_en, text_np = quizzer.extract_text()
                        if text_en is not None:
                            dictionary_maker.dict_update(chapter["_id"], text_en, client)
                st.success("Updated dictionary in MongoDB for selected chapters")


if __name__ == '__main__':
    try:
        cfg = ConfigInit()
        ChaptersUI(cfg)
    except Exception as e:
        st.error(str(e))
