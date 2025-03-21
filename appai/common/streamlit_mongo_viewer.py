import streamlit as st
from pymongo import MongoClient
import pandas as pd

def mongodb_viewer(client_uri: str, database_name: str, collection_name: str, filters=None, columns=None, hidden_columns=[]) -> list:
    """
    Displays a read-only data table with a single checkbox that edits a 'selected' column for row selection.

    Args:
        client_uri (str): MongoDB connection string.
        database_name (str): Database name.
        collection_name (str): Collection name.
        filters (dict, optional): MongoDB query filter.
        columns (list, optional): List of column names to display in the table.

    Returns:
        list[dict]: List of selected documents.
    """
    # Connect to MongoDB
    client = MongoClient(client_uri)
    db = client[database_name]
    collection = db[collection_name]

    # Apply filters if provided
    if filters:
        query = filters
    else:
        query = {}

    # Apply projection (columns to display) if specified
    if columns:
        projection = {col: 1 for col in columns}  # Include only specified columns
    else:
        projection = None  # If no columns specified, fetch all fields

    # Fetch documents from MongoDB
    cursor = collection.find(query, projection)

    # Convert the cursor to a list of documents
    documents = list(cursor)

    # Close the MongoDB connection
    client.close()

    # Convert documents to a pandas DataFrame for easy table manipulation
    df = pd.DataFrame(documents)

    # Add a 'selected' column, initialized to False
    df['selected'] = False

    # Display the table with the 'selected' column
    selected_docs = []
    if not df.empty:
        # Add a search bar to filter the DataFrame
        search_query = st.text_input("Search", "", key=collection_name+"_search")

        if search_query:
            # Filter the DataFrame based on the search query (case insensitive)
            df = df[df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]

        # Create the checkbox at the top to toggle all selections
        toggle_all = st.checkbox("Select/Deselect All", key=collection_name+"_toggle_all")

        # Update the 'selected' column based on the toggle checkbox
        df['selected'] = toggle_all

        # Show the updated DataFrame with 'selected' column
        edited_df = st.data_editor(df, disabled=columns, column_order=["selected", *columns])  # Drop the '_id' column for display, optional

        # Collect selected documents where 'selected' is True
        selected_docs = edited_df[edited_df['selected']].to_dict(orient='records')
    return selected_docs

# Sample usage within a Streamlit app
if __name__ == "__main__":
    st.title("MongoDB Viewer")

    client_uri = 'mongodb://localhost:27017'
    database_name = 'mydb'
    collection_name = 'mycollection'

    filters = {}  # Adjust filters as needed
    columns = ['name', 'age', 'email']  # Adjust columns to display

    selected_docs = mongodb_viewer(client_uri, database_name, collection_name, filters, columns)

    if selected_docs:
        st.write("### Selected Documents", selected_docs)
    else:
        st.write("No documents selected.")