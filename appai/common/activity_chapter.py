import re

from langchain_huggingface import HuggingFaceEmbeddings
from pymongo.synchronous.database import Database

from .activity import Activity, download_pdf, extract_text_from_pdf


# Pass one of textbook or mongo. If textbook is None then mongo must be provided and the function will look up the
# textbook for you.
def chapter_url_from_id(chapter_id: str, textbook: dict | None, mongo: Database | None):
    groups = re.search(r"([1-9]|10|11|12)(EN|ENa|Sa|S|SF|Ma|M|SSa|SS|N|H|V|CS)[0-9]{2}(\.[0-9]{2})?",
                       chapter_id, re.IGNORECASE)
    grade_level = groups[1]  # grade level
    subject = groups[2]
    textbook = textbook if textbook is not None else mongo.textbooks.find_one({"prefix": grade_level + subject})
    url = f"https://looma.website/content/chapters/{textbook['fp'].removeprefix("textbooks/")}textbook_chapters/{chapter_id}.pdf"
    return url, textbook


class ChapterActivity(Activity):

    def embed(self, mongo: Database, embeddings: HuggingFaceEmbeddings) -> list[float]:
        # activity['ID'] is the chapter ID (not the activity objectid)
        url, _ = chapter_url_from_id(self.activity['ID'], textbook=None, mongo=mongo)
        pdf_stream = download_pdf(url)
        text = extract_text_from_pdf(pdf_stream)
        return embeddings.embed_query(text)

    def payload(self) -> dict:
        return {
            "collection": "activities",
            "source_id": str(self.activity['_id']),
            "title": self.activity['dn'],
            "ft": "chapter",
            "chapter_id": self.activity['ID']
        }
