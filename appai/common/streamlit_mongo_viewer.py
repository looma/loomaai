import uuid
import pandas as pd
import streamlit as st
from pymongo import MongoClient


def mongodb_viewer(client_uri, database_name, collection_name, filters=None, columns=None) -> list[dict]:
    """
    Args:
        client_uri (str): MongoDB connection string.
        database_name (str): Database name.
        collection_name (str): Collection name.
        filters (dict): MongoDB query filter.
        columns (list): List of column names to display in the table.

    Returns:
        list[dict]: List of selected documents.
    """
    client = MongoClient(client_uri)
    db = client[database_name]
    collection = db[collection_name]

    filters = filters or {}
    documents = list(collection.find(filters))

    if not documents:
        st.warning("No documents found.")
        return []

    if not columns:
        columns = list(documents[0].keys())

    if '_id' not in columns:
        columns.insert(0, '_id')

    data = pd.DataFrame([{k: v for k, v in doc.items() if k in columns} for doc in documents])
    data['_id'] = data['_id'].astype(str)

    # Add a "Select All" checkbox in the header
    select_all = st.checkbox("Select All", key="select_all")

    # Initialize "Select" column with the value of the "Select All" checkbox
    data["Select"] = select_all

    search_query = st.text_input("Search", placeholder="Type to filter results...", key=str(uuid.uuid4()))

    if search_query:
        filtered_data = data[data.apply(
            lambda row: search_query.lower() in row.astype(str).str.lower().to_string(), axis=1
        )]
    else:
        filtered_data = data

    edited_data = st.data_editor(
        filtered_data,
        column_config={
            "Select": st.column_config.CheckboxColumn("Select Rows"),
        },
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
    )

    # Collect selected documents (entire documents, not just IDs)
    selected_documents = edited_data.loc[edited_data["Select"], "_id"].apply(
        lambda selected_id: next((doc for doc in documents if str(doc['_id']) == selected_id), {})
    ).tolist()

    return selected_documents