import streamlit as st
from common.split import *
from common.config import ConfigInit
from qdrant_client import QdrantClient, models
from common.streamlit_mongo_viewer import mongodb_viewer
from common.embed import objectid_to_uuid

def remove_textbook(mongo, qdrant, textbooks):
    for textbook_prefix in textbooks:
        # get list of chapters with this prefix
        chapter_activities = list(mongo['activities'].find({'ft': "chapter", 'ID': re.compile(fr"^{textbook_prefix}\d", re.IGNORECASE)}))
        # remove chapter from qdrant
        qdrant.delete(
            collection_name="activities",
            points_selector=models.PointIdsList(
                points=[objectid_to_uuid(str(chapter['_id'])) for chapter in chapter_activities],
            ),
        )

        for chapter in chapter_activities:
            chapter_id = chapter['ID']
            update = {
                "$pull": {"ch_id": chapter_id}
            }
            mongo['activities'].update_many({"ch_id": {"$type": "array"}}, update)
            # remove chapter from mongodb activities
            mongo['activities'].delete_one({'ID': chapter_id})
            # remove chapter from mongodb chapters
            mongo['chapters'].delete_one({'_id': chapter_id})
        mongo['textbooks'].delete_one({'prefix': textbook_prefix})



def TextbookUI(cfg):
    config = cfg.json()
    st.title('Textbook')

    MONGO_URI=f'mongodb://{config["mongo"]["host"]}:{config["mongo"]["port"]}'
    DATABASE_NAME = f'{config["mongo"]["database"]}'
    FILTERS = {}
    selected = mongodb_viewer(
        client_uri=MONGO_URI,
        database_name=DATABASE_NAME,
        collection_name="textbooks",
        filters=FILTERS,
        columns=["prefix", "dn"]
    )

    textbooks = [t['prefix'] for t in selected]

    split_text, remove, dict, embed = st.tabs(['Split Textbook', 'Remove Textbook', 'Dictionary', 'Embed'])

    with split_text:
        st.info("This will create separate PDFs for every chapter in the selected textbooks. The location of the created PDFs will be displayed here.")
        if st.button("Split Into Chapters"):
            try:
                with st.spinner("Splitting..."):
                    #gets the directory that the chapters have to go to
                    datadir = config["datadir"]
                    #calls the MongoClient and runs the split function in loomaai/appai/common/split.py
                    client = MongoClient(MONGO_URI)
                    split(client, datadir, textbooks)
                st.success(f"Split {len(textbooks)} textbooks and saved split PDFs to {datadir}")
            except Exception as exception:
                st.error(f"Error splitting textbooks {exception}")

    with remove:
        st.warning("For each selected textbook, this will PERMANENTLY remove from MongoDB and Qdrant: the textbook, all its chapters, and any relationships to activities")
        if st.button("Remove Permanently"):
            try:
                with st.spinner("Removing..."):
                    client = MongoClient(MONGO_URI)
                    qd = QdrantClient(url=f'http://{config["qdrant"]["host"]}:{config["qdrant"]["port"]}')
                    remove_textbook(client.get_database('looma'), qd, textbooks)
                st.success(f"Removed {textbooks} textbooks from Qdrant")
            except Exception as exception:
                st.error(f"Error removing textbooks {exception}")

    with dict:
        st.write('hi')

    with embed:
        st.write('hi')




if __name__ == '__main__':
    try:
        cfg = ConfigInit()
        TextbookUI(cfg)
    except Exception as e:
        st.error(str(e))
