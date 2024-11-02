import re

import bson
import requests
from langchain_qdrant import QdrantVectorStore
from pymongo import MongoClient

from langchain_huggingface import HuggingFaceEmbeddings
from bs4 import BeautifulSoup
from qdrant_client import QdrantClient
from qdrant_client import models
import requests
import fitz  # PyMuPDF
from io import BytesIO


def download_pdf(url):
    response = requests.get(url)
    response.raise_for_status()
    return BytesIO(response.content)


def extract_text_from_pdf(pdf_stream):
    pdf_document = fitz.open(stream=pdf_stream, filetype="pdf")
    text = ""

    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()

    pdf_document.close()
    return text


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


# only use for ft=chapter
def populate_relevant_resources(mongo_client: MongoClient, vector_db: QdrantClient):
    offset = None
    while True:
        (results, offset) = vector_db.scroll(
            collection_name="activities",  # Replace with your collection name
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(key="ft",
                                          match=models.MatchValue(value="chapter")),
                ]
            ),
            limit=10,
            with_vectors=True,
            offset=offset
        )

        for chapter in results:
            try:
                similar_docs = vector_db.query_points(collection_name="activities", query=chapter.vector,
                                                      with_payload=True,
                                                      query_filter=models.Filter(
                                                          must_not=[
                                                              models.FieldCondition(key="ft",
                                                                                    match=models.MatchValue(
                                                                                        value="chapter")),
                                                          ]
                                                      ), limit=10)

                for activity in similar_docs.points:
                    try:
                        mongo_client.get_database("looma").get_collection("activities").update_one(
                            {"_id": bson.ObjectId(activity.payload["source_id"])},
                            {"$addToSet": {"ch_id": chapter.payload["chapter_id"]}})
                        print(f"Updated relevant resources for chapter {chapter.payload['chapter_id']}")
                    except Exception as e:
                        print(f"Error updating activity {activity.payload['source_id']}: {e}")
            except Exception as e:
                print(f"Error processing chapter {chapter.payload['chapter_id']}: {e}")

        if offset is None:
            print("Done")
            return


from alive_progress import alive_bar
from concurrent.futures import ThreadPoolExecutor, as_completed


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
            futures = {executor.submit(process_activity, activity, hf, vector_db, db): activity for activity in
                       activities}

            # Ensure all futures complete and get the result (if needed)
            for future in as_completed(futures):
                activity = futures[future]
                try:
                    future.result()  # Get the result if needed, or handle any exceptions
                except Exception as e:
                    print("Error: ", e, "Activity:", activity["_id"])
                progress_bar()
        for activity in activities:
            process_activity(activity, hf, vector_db, db)


# db argument is the mongo looma database (not client)
def process_activity(activity, hf: HuggingFaceEmbeddings, vector_db: QdrantClient, db):
    match activity['ft']:
        case "chapter":
            # activity['ID'] is the chapter ID (not the activity objectid)
            groups = re.search(r"([1-9]|10|11|12)(EN|ENa|Sa|S|SF|Ma|M|SSa|SS|N|H|V|CS)[0-9]{2}(\.[0-9]{2})?",
                               activity['ID'], re.IGNORECASE)
            grade_level = groups[1]  # grade level
            subject = groups[2]
            textbook = db.textbooks.find_one({"prefix": grade_level + subject})
            url = f"https://looma.website/content/chapters/{textbook['fp'].removeprefix("textbooks/")}textbook_chapters/{activity['ID']}.pdf"

            pdf_stream = download_pdf(url)
            text = extract_text_from_pdf(pdf_stream)

            embeddings = hf.embed_query(text)

            vector_db.upsert("activities", points=[
                models.PointStruct(
                    id=objectid_to_uuid(str(activity['_id'])),
                    vector={"text-body": embeddings, "text-title": hf.embed_query(activity['dn'])},
                    payload={"key1": activity.get("key1", ""), "collection": "activities",
                             "source_id": str(activity['_id']), "title": activity['dn'], "ft": "chapter",
                             "chapter_id": activity['ID']},
                ),
            ])

            print(f"[] [Added chapter to vector DB]", url)
        case "html":
            url = f"http://looma.website/{activity['fp']}{activity['fn']}"
            text = get_visible_text(url)

            embeddings = hf.embed_query(text)

            vector_db.upsert("activities", points=[
                models.PointStruct(
                    id=objectid_to_uuid(str(activity['_id'])),
                    vector={"text-body": embeddings, "text-title": hf.embed_query(activity['dn'])},
                    payload={"key1": activity.get("key1", ""), "collection": "activities",
                             "source_id": str(activity['_id']), "title": activity['dn'], "ft": "html"},
                ),
            ])

            print(f"[] [Added document to vector DB]", url)
        case "mp4":
            # TODO: video embedding
            pass
        case "pdf":
            # https://looma.website/content/pdfs/What_Time_Do_You.pdf
            fp = activity['fp'] if 'fp' in activity else '../content/pdfs/'
            url = f"https://looma.website/{fp}{activity['fn']}"
            pdf_stream = download_pdf(url)
            text = extract_text_from_pdf(pdf_stream)

            embedded = hf.embed_query(text)

            vector_db.upsert("activities", points=[
                models.PointStruct(
                    id=objectid_to_uuid(str(activity['_id'])),
                    vector={"text-body": embedded, "text-title": hf.embed_query(activity['dn'])},
                    payload={"key1": activity.get("key1", ""), "collection": "activities",
                             "source_id": str(activity['_id']), "title": activity['dn'], "ft": "pdf"},
                ),
            ])
            print(f"[] [Added PDF to vector DB]", url)


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
