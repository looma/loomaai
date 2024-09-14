import requests
from langchain_qdrant import QdrantVectorStore
from pymongo import MongoClient

from langchain_huggingface import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from bs4 import BeautifulSoup
from qdrant_client import QdrantClient
from qdrant_client import models


def get_visible_text(url):
    try:
        # Fetch the HTML content from the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract visible text
        # Get text from all tags and strip extra whitespace
        text = soup.get_text(separator='\n', strip=True)

        return text

    except requests.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None


def generate_vectors(llm, mongo_client: MongoClient, vector_db: QdrantClient):
    db = mongo_client.get_database("looma")
    activities_collection = db.get_collection("activities")

    activities = activities_collection.find({"ft": "html"})
    print(f'{activities_collection.count_documents({"ft": "html"})} activities to be processed')

    for i, activity in enumerate(activities):
        try:
            match activity['ft']:
                case "html":
                    url = f"http://looma.website/{activity['fp']}{activity['fn']}"
                    print(url)
                    text = get_visible_text(url)
                    model_name = "sentence-transformers/all-mpnet-base-v2"
                    model_kwargs = {}
                    encode_kwargs = {'normalize_embeddings': False}
                    hf = HuggingFaceEmbeddings(
                        model_name=model_name,
                        model_kwargs=model_kwargs,
                        encode_kwargs=encode_kwargs
                    )

                    vector_db.upsert("activities", points=[
                        models.PointStruct(
                            id=objectid_to_uuid(str(activity['_id'])),
                            vector=hf.embed_query(text),
                            payload={"key1": activity.get("key1", ""), "collection": "activities",
                                     "source_id": str(activity['_id']), "title": activity['dn']},
                        ),
                    ])

                    print(f"[{i}] [Added document to vector DB]", url)
                case "mp4":
                    # TODO: video embedding
                    pass
                case "pdf":
                    # TODO: pdf embedding
                    pass

        except Exception as e:
            print("Error: ", e, "Chapter:", activity["_id"])


def create_collection_if_not_exists(collection_name: str, client: QdrantClient):
    # Check if the collection exists
    collections = client.get_collections()
    existing_collections = [collection.name for collection in collections.collections]

    if collection_name in existing_collections:
        print(f"Collection '{collection_name}' already exists.")
        return
    # Create the collection
    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
    )

    print(f"Collection '{collection_name}' created successfully.")

def objectid_to_uuid(objectid):
    """
    Convert a 24-character ObjectId (hexadecimal string) to a UUID format.

    Parameters:
    - objectid (str): A 24-character hexadecimal string.

    Returns:
    - str: A UUID string in the format `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`.
    """
    # Validate the length of the input
    if len(objectid) != 24:
        raise ValueError("ObjectId must be a 24-character hexadecimal string.")

    # Pad the ObjectId to 32 characters (for UUID format)
    padded_objectid = objectid.ljust(32, '0')

    # Format the padded ObjectId into UUID format
    uuid = f"{padded_objectid[0:8]}-{padded_objectid[8:12]}-{padded_objectid[12:16]}-{padded_objectid[16:20]}-{padded_objectid[20:32]}"

    return uuid

def uuid_to_objectid(uuid):
    """
    Convert a UUID string to a 24-character ObjectId (hexadecimal string).

    Parameters:
    - uuid (str): A UUID string in the format `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`.

    Returns:
    - str: A 24-character hexadecimal string (ObjectId).
    """
    # Validate the UUID format
    if len(uuid) != 36 or uuid[8] != '-' or uuid[13] != '-' or uuid[18] != '-' or uuid[23] != '-':
        raise ValueError("Invalid UUID format. Expected format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.")

    # Remove dashes from the UUID
    objectid = uuid.replace('-', '')

    # Ensure the ObjectId is exactly 24 characters long
    if len(objectid) > 24:
        objectid = objectid[:24]  # Truncate to 24 characters
    elif len(objectid) < 24:
        objectid = objectid.ljust(24, '0')  # Pad with zeros if necessary

    return objectid