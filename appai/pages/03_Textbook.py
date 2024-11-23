import streamlit as st

from common.streamlit_mongo_viewer import mongodb_viewer

if __name__ == "__main__":
    st.title("MongoDB Viewer")

    MONGO_URI = "mongodb://host.docker.internal:47017"
    DATABASE_NAME = "looma"
    COLLECTION_NAME = "chapters"

    FILTERS = {}

    selected = mongodb_viewer(
        client_uri=MONGO_URI,
        database_name=DATABASE_NAME,
        collection_name=COLLECTION_NAME,
        filters=FILTERS,
        columns=["_id", "dn"]
    )

    st.write("Selected documents:", selected)
#
# if __name__ == '__main__':
#     try:
#         cfg = ConfigInit()
#         TextbookUI(cfg)
#     except Exception as e:
#         st.error(str(e))

