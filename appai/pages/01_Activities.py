import os

import streamlit as st
import requests
from io import BytesIO
import logging

# Qdrant server configuration

COLLECTION_NAME = "activities"

# Function to create a snapshot of the specified collection
def create_snapshot( collection_name):
    QDRANT_URL = os.getenv("QDRANT_URL")
    snapshot_endpoint = f"{QDRANT_URL}/collections/{collection_name}/snapshots"
    try:
        # Send a request to create a snapshot
        response = requests.post(snapshot_endpoint)
        response.raise_for_status()
        snapshot_info = response.json()
        return snapshot_info
    except requests.exceptions.RequestException as e:
        st.error(f"Error creating snapshot: {e}")
        return None

# Function to download the snapshot file
def download_snapshot(snapshot_location):
    # config = cfg.json()
    # QDRANT_URL = f"http://{config['qdrant']['host']}:{config['mongo']['port']}"
    # COLLECTION_NAME = "activities"
    try:
        # Fetch the snapshot file from the provided location
        # Fetch the snapshot file from the provided location
        response = requests.get(snapshot_location)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        st.error(f"Error downloading snapshot: {e}")
        return None

# Streamlit App
def main():
    st.title("Activities")
    st.header("Generate Embeddings")
    st.markdown("""
    For performance reasons, it is not supported to generate embeddings from Streamlit (i.e. inside a docker container). On an M1 Pro MacBook Pro (2021), the process takes about 30 minutes total for all resources. To generate embeddings: 
    * Clone https://github.com/looma/Looma-II and follow the setup instructions in the README
    * Clone https://github.com/looma/loomaai and follow the setup instructions in the README
    * From the loomaai root directory, run `python3 -m appai.common.embed`
    """)
    st.header("Download Snapshot")
    st.markdown(
        """
        This tool allows you to create a snapshot of the **activities** collection in Qdrant and download it, for example to load onto a looma box.
        """
    )

    if st.button(f"Create and Download Snapshot of '{COLLECTION_NAME}' Collection"):
        st.info("Creating snapshot, please wait...")
        snapshot_info = create_snapshot(COLLECTION_NAME)

        if snapshot_info:
            st.text(snapshot_info)
            snapshot_name = snapshot_info.get("result", {}).get("name")
            if snapshot_name:
                QDRANT_URL = os.getenv("QDRANT_URL")
                snapshot_endpoint = f"{QDRANT_URL}/collections/{COLLECTION_NAME}/snapshots/{snapshot_name}"
                st.success("Snapshot created successfully. Downloading...")
                snapshot_data = download_snapshot(snapshot_location=snapshot_endpoint)

                if snapshot_data:
                    # Prepare the snapshot data for download
                    buffer = BytesIO(snapshot_data)
                    buffer.seek(0)
                    st.download_button(
                        label=f"Download {COLLECTION_NAME} Snapshot",
                        data=buffer,
                        file_name=f"{COLLECTION_NAME}_snapshot.snapshot",
                        mime="application/octet-stream"
                    )
            else:
                st.error("Snapshot location not found in the response.")
        else:
            st.error("Failed to create the snapshot.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(str(e))
        logging.error(str(e))
        st.stop()