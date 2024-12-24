from pymongo import MongoClient

from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from qdrant_client import models

from .activity import Activity
from .activity_pdf import PdfActivity
from .activity_html import HtmlActivity
from .activity_chapter import ChapterActivity

from alive_progress import alive_bar
from concurrent.futures import ThreadPoolExecutor, as_completed
from pymongo.database import Database

def generate_vectors(mongo_client: MongoClient, vector_db: QdrantClient):
    db = mongo_client.get_database("looma")
    activities_collection = db.get_collection("activities")

    activities = activities_collection.find({"ft": {"$in": ["chapter", "html", "pdf"]}})

    model_name = "sentence-transformers/all-mpnet-base-v2"
    model_kwargs = {}
    encode_kwargs = {'normalize_embeddings': False}
    hf = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )

    with alive_bar(activities_collection.count_documents({"ft": {"$in": ["chapter", "html", "pdf"]}})) as progress_bar:
        # Use ThreadPoolExecutor to speed up the loop
        with ThreadPoolExecutor() as executor:
            # Submit tasks to the pool
            futures = {}

            for activity in activities:
                ac: Activity
                if activity["ft"] == "html":
                    ac = HtmlActivity(activity)
                if activity["ft"] == "pdf":
                    ac = PdfActivity(activity)
                if activity["ft"] == "chapter":
                    ac = ChapterActivity(activity)
                futures[executor.submit(process_activity, ac, hf, vector_db, db)] = ac

            # Ensure all futures complete and get the result (if needed)
            for future in as_completed(futures):
                activity = futures[future]
                try:
                    future.result()  # Get the result if needed, or handle any exceptions
                    print(f"[Success]", activity.activity['_id'])
                except Exception as e:
                    print("[Error]", e, "Activity:", activity.activity["_id"])
                progress_bar()

def process_activity(activity: Activity, hf: HuggingFaceEmbeddings, vector_db: QdrantClient, db: Database):
    embeddings = activity.embed(mongo=db, embeddings=hf)
    payload = activity.payload()
    vector_db.upsert("activities", points=[
        models.PointStruct(
            id=objectid_to_uuid(str(activity.activity['_id'])),
            vector={"text-body": embeddings, "text-title": hf.embed_query(activity.activity.get('dn', ''))},
            payload=payload
        ),
    ])

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
        vectors_config={"text-body": models.VectorParams(
            size=768,  # OpenAI Embeddings
            distance=models.Distance.COSINE,
        ), "text-title": models.VectorParams(
            size=768,  # OpenAI Embeddings
            distance=models.Distance.COSINE,
        )},
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
