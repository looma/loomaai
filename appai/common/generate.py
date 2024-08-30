import re

import requests
from pymongo import MongoClient

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from pathlib import Path
from bs4 import BeautifulSoup

from .summary import extract_text_from_pdf, summarize_text

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

def generate_vectors(llm, mongo_client: MongoClient, data_dir: str):
    model_name = "sentence-transformers/all-mpnet-base-v2"
    model_kwargs = {}
    encode_kwargs = {'normalize_embeddings': False}
    hf = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )

    db = mongo_client.get_database("looma")
    chapters_collection = db.get_collection("chapters")
    activities_collection = db.get_collection("activities")

    faiss_db = None
    Path(f'{data_dir}/vector_db').mkdir(parents=True, exist_ok=True)
    chapters = chapters_collection.find({"pn": {"$ne": ""}})
    print(f'{chapters_collection.count_documents({"pn": {"$ne": ""}})} chapters to be processed')

    activities = activities_collection.find({"ft": "html"})
    print(f'{activities_collection.count_documents({"ft": "html"})} activities to be processed')

    # for i, chapter in enumerate(chapters):
    #     try:
    #         groups = re.search(r"([1-9]|10|11|12)(EN|ENa|Sa|S|SF|Ma|M|SSa|SS|N|H|V|CS)[0-9]{2}(\.[0-9]{2})?",
    #                            chapter['_id'], re.IGNORECASE)
    #         grade_level = groups[1]  # grade level
    #         subject = groups[2]
    #         firstPage = chapter['pn']
    #         lastPage = chapter['pn'] + chapter['len']
    #         if firstPage == "" or lastPage == "":
    #             continue
    #         textbook = db.textbooks.find_one({"prefix": grade_level + subject})
    #         subpath = f"/files/chapters/{textbook['fp']}textbook_chapters/{chapter['_id']}.pdf"
    #         url = f"{data_dir}{subpath}"
    #         text = extract_text_from_pdf(url, "English")
    #         summary = summarize_text(llm, text, "English")
    #         final_docs = [Document(page_content=summary,
    #                                metadata={"collection": "chapters", "source_id": textbook['_id']})]
    #         if faiss_db is None:
    #             faiss_db = FAISS.from_documents(final_docs, hf)
    #         faiss_db.add_documents(final_docs)
    #         faiss_db.save_local(f"{data_dir}/vector_db")
    #         print(f"[{i}] [Added document to FAISS]", url, firstPage, lastPage)
    #     except Exception as e:
    #         print("Error: ", e, "Chapter:", chapter["_id"])

    for i, activity in enumerate(activities):
        try:
            match activity['ft']:
                case "html":
                    url = f"http://looma.website/{activity['fp']}{activity['fn']}"
                    print(url)
                    text = get_visible_text(url)
                    # summary = summarize_text(llm, text, "English")
                    final_docs = [Document(page_content=text,
                                           metadata={"collection": "activities", "source_id": activity['_id'], "title": activity['dn']})]
                    if faiss_db is None:
                        faiss_db = FAISS.from_documents(final_docs, hf)
                    faiss_db.add_documents(final_docs)
                    faiss_db.save_local(f"{data_dir}/vector_db")
                    print(f"[{i}] [Added document to FAISS]", url)
                case "mp4":
                    # TODO: video embedding
                    pass
                case "pdf":
                    # TODO: pdf embedding
                    pass

        except Exception as e:
            print("Error: ", e, "Chapter:", activity["_id"])
