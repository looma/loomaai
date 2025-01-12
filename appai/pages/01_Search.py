import streamlit as st
from qdrant_client import QdrantClient

from common.config import ConfigInit
from common.query import query

def search_qdrant(q, qdrant_client):
    # Perform the search query in Qdrant. Adjust collection_name and other params based on your setup.
    try:
        results = query(q, qdrant_client)
    except Exception as e:
        results = []
        if "404" in str(e):
            st.error("The activities collection does not exist in qdrant. Please click on \"Activities\" in the sidebar for instructions.")
    return results

def display_results(results):
    # Display search results in a human-readable format
    if results:
        for result in results.points:
            st.write(f"Score: {result.score}")
            st.write(f"ID: {result.id}")
            st.write(f"Payload: {result.payload}")
            st.write("---")
    else:
        st.write("No results found.")

def QdrantSearchUI(cfg):
    config = cfg.json()
    st.title('Qdrant Search')

    # Initialize Qdrant client
    qdrant_client = QdrantClient(url=f'http://{config["qdrant"]["host"]}:{config["qdrant"]["port"]}')

    # Input: Search query from the user
    q = st.text_input("Enter your search query:")

    if q:
        try:
            # Perform the query
            with st.spinner("Searching..."):
                results = search_qdrant(q, qdrant_client)
                # Display results
                display_results(results)
        except Exception as e:
            st.error(f"Error while querying Qdrant: {e}")

if __name__ == '__main__':
    try:
        cfg = ConfigInit()
        QdrantSearchUI(cfg)
    except Exception as e:
        st.error(str(e))