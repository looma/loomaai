import re

from pymongo import MongoClient

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from pathlib import Path

from chapter_summaries.summary import extract_text, query_llm

def generate_vectors(llm):
    model_name = "sentence-transformers/all-mpnet-base-v2"
    model_kwargs = {}
    encode_kwargs = {'normalize_embeddings': False}
    hf = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )

    client = MongoClient("mongodb://localhost:47017/")
    db = client.get_database("looma")
    collection = db.get_collection("chapters")

    faiss_db = None
    Path('../loomadata/vector_db').mkdir(parents=True, exist_ok=True)

    for chapter in collection.find({"pn": {"$ne": ""}}):
        try:
            groups = re.search(r"([1-9]|10|11|12)(EN|ENa|Sa|S|SF|Ma|M|SSa|SS|N|H|V|CS)[0-9]{2}(\.[0-9]{2})?",
                               chapter['_id'], re.IGNORECASE)
            grade_level = groups[1]  # grade level
            subject = groups[2]
            firstPage = chapter['pn']
            lastPage = chapter['pn'] + chapter['len']
            if firstPage == "" or lastPage == "":
                continue
            textbook = db.textbooks.find_one({"prefix": grade_level + subject})

            url = f"../{textbook['fp']}textbook_chapters/{chapter['_id']}.pdf"
            text = extract_text(url)
            summary = query_llm(llm, text)
            final_docs = [Document(page_content=summary, metadata={"source": url, "firstPage": firstPage, "lastPage": lastPage})]
            if faiss_db is None:
                faiss_db = FAISS.from_documents(final_docs, hf)
            faiss_db.add_documents(final_docs)
            faiss_db.save_local("../loomadata/vector_db")
            print("[Added document to FAISS]", url, firstPage, lastPage)
        except Exception as e:
            print("Error: ", e, "Chapter:", chapter["_id"])
