from abc import ABC, abstractmethod
from io import BytesIO
import requests
import fitz
from langchain_huggingface import HuggingFaceEmbeddings
from pymongo.database import Database

class Activity(ABC):
    def __init__(self, activity: dict):
        self.activity = activity
        self.cl_lo = activity.get("cl_lo", None)
        self.cl_hi = activity.get("cl_hi", None)
        self.cl_official = activity.get("cl_official", None)

    @abstractmethod
    def embed(self, mongo: Database, embeddings: HuggingFaceEmbeddings) -> list[float]:
        pass

    @abstractmethod
    def payload(self) -> dict:
        pass

    @abstractmethod
    def get_text(self, mongo: Database) -> str:
        pass


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
