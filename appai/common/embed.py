import re

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

from .activity_video import VideoActivity
from readability import Readability


def generate_vectors(mongo_client: MongoClient, vector_db: QdrantClient, missing_only: bool):
    db = mongo_client.get_database("looma")
    activities_collection = db.get_collection("activities")
    activities = activities_collection.find({"ft": {"$in": ["chapter", "html", "pdf", "video"]}})

    model_name = "sentence-transformers/all-mpnet-base-v2"
    model_kwargs = {}
    encode_kwargs = {'normalize_embeddings': False}
    hf = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )

    successes = 0
    no_reading_level = 0
    errors = 0

    with alive_bar(activities_collection.count_documents(
            {"ft": {"$in": ["chapter", "html", "pdf", "video"]}})) as progress_bar:
        # Use ThreadPoolExecutor to speed up the loop
        # with ThreadPoolExecutor() as executor:
            # Submit tasks to the pool
            # futures = {}

        for activity in activities:
            try:
                ac: Activity
                if activity["ft"] == "html":
                    ac = HtmlActivity(activity)
                if activity["ft"] == "pdf":
                    ac = PdfActivity(activity)
                if activity["ft"] == "chapter":
                    ac = ChapterActivity(activity)
                if activity["ft"] == "video":
                    ac = VideoActivity(activity)
                # futures[executor.submit(process_activity, ac, hf, vector_db, db, missing_only)] = ac
            # Ensure all futures complete and get the result (if needed)
            # for future in as_completed(futures):
            #     activity = futures[future]
                process_activity(ac, hf, vector_db, db, missing_only)
                # future.result()  # Get the result if needed, or handle any exceptions
                print(f"[Success]", ac.activity['_id'])
                successes += 1
            except Exception as e:
                print("[Error]", e, "Activity:", ac.activity["_id"])
                errors += 1
            progress_bar()
        print("Successes: ", successes)
        print("Errors: ", errors)


def process_activity(activity: Activity, hf: HuggingFaceEmbeddings, vector_db: QdrantClient, db: Database,
                     missing_only: bool):
    if missing_only and len(
            vector_db.retrieve("activities", ids=[objectid_to_uuid(str(activity.activity['_id']))])) > 0:
        print(f"Skipping {activity.activity['_id']}")
        return

    text = activity.get_text(mongo=db)
    payload = activity.payload()
    cl_lo = 0
    cl_hi = 13

    try:
        r = Readability(text)
        grade = int(r.flesch_kincaid().grade_level)
        if grade:
            cl_lo = grade - 1
            cl_hi = grade + 1
            # detected_range = prompt_text(ChatOpenAI(),
            #                          "You are a school teacher in Nepal deciding which grade level (1-12) this educational resource is appropriate for. Refer to nepalese educational standards in your decision. What is the minimum and maximum grade level (1-12) you would use this resource for? Return only two numerical numbers between 1 and 12, separated by a comma (min and max grade). No words or other characters. Here is the resource:  {text}",
            #                          text).removeprefix("```").removesuffix("```")

            # cl_lo, cl_hi = map(int, detected_range.split(","))

            db.get_collection("activities").update_one({"_id": activity.activity['_id']},
                                                           {"$set": {"cl_lo": cl_lo, "cl_hi": cl_hi}})
    except Exception as e:
        print(f"Error determining grade level for activity {activity.activity['_id']}: {e}")

    payload["cl_lo"] = cl_lo
    payload["cl_hi"] = cl_hi

    embeddings = activity.embed(mongo=db, embeddings=hf)

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
