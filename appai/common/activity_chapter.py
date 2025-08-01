import io
import re

from langchain_huggingface import HuggingFaceEmbeddings
from pymongo.synchronous.database import Database

from .activity import Activity, download_pdf, extract_text_from_pdf


# Pass one of textbook or mongo. If textbook is None then mongo must be provided and the function will look up the
# textbook for you.
# Returns: english looma.website URL, english local path, nepali looma.website URL, nepali local path, textbook object
def chapter_url_from_id(chapter_id: str, files_dir: str, textbook: dict | None, mongo: Database | None) -> (str, str, dict):
    groups = re.search(r"([1-9]|10|11|12)(EN|ENa|Sa|S|SF|Ma|M|SSa|SS|N|H|V|CS)[0-9]{2}(\.[0-9]{2})?",
                       chapter_id, re.IGNORECASE)
    grade_level = groups[1]  # grade level
    subject = groups[2]
    textbook = textbook if textbook is not None else mongo.textbooks.find_one({"prefix": grade_level + subject})
    url_en = None
    local_path_en = None
    url_np = None
    local_path_np = None
    if textbook['fn'] != '':
        # TODO: remote url_en and url_np are for the whole textbook. We should never embed the whole textbook in the context of a single chapter. Will need to upload final split to looma.website for this
        # local path is correct (for the single chapter)
        url_en = f"https://looma.website/content/textbooks/{textbook['fp']}{textbook['fn']}"
        local_path_en = f"{files_dir}/{textbook["fp"]}{'en'}/{chapter_id}.pdf"
    if textbook['nfn'] != '':
        url_np = f"https://looma.website/content/textbooks/{textbook['fp']}{textbook['nfn']}"
        local_path_np = f"{files_dir}/{textbook["fp"]}{'np'}/{chapter_id}-nepali.pdf"
    return url_en, local_path_en, url_np, local_path_np, textbook


class ChapterActivity(Activity):

    def __init__(self, activity: dict):
        super().__init__(activity)
        groups = re.search(r"([1-9]|10|11|12)(EN|ENa|Sa|S|SF|Ma|M|SSa|SS|N|H|V|CS)[0-9]{2}(\.[0-9]{2})?",
                           activity.get("ID"), re.IGNORECASE)
        grade_level = groups[1]  # grade level
        self.cl_official = int(grade_level)

    def get_text(self, mongo: Database, ) -> str:
        # activity['ID'] is the chapter ID (not the activity objectid)
        _, filename_en, _, filename_np, _ = chapter_url_from_id(self.activity['ID'], files_dir='', textbook=None, mongo=mongo)
        if filename_en is not None:
            with open("data"+filename_en, "rb") as file:
                pdf_stream = io.BytesIO(file.read())
                return extract_text_from_pdf(pdf_stream)

        return ""

    def embed(self, mongo: Database, embeddings: HuggingFaceEmbeddings) -> list[float]:
        return embeddings.embed_query(self.get_text(mongo))

    def payload(self) -> dict:

        return {
            "collection": "activities",
            "source_id": str(self.activity['_id']),
            "title": self.activity['dn'],
            "ft": "chapter",
            "chapter_id": self.activity['ID'],
            "cl_official": self.cl_official,
        }
