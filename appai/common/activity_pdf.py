from langchain_huggingface import HuggingFaceEmbeddings
from pymongo.synchronous.database import Database

from .activity import Activity, download_pdf, extract_text_from_pdf


class PdfActivity(Activity):
    def embed(self, mongo: Database, embeddings: HuggingFaceEmbeddings) -> list[float]:
        fp = self.activity['fp'] if 'fp' in self.activity else '../content/pdfs/'
        url = f"https://looma.website/{fp}{self.activity['fn']}"
        pdf_stream = download_pdf(url)
        text = extract_text_from_pdf(pdf_stream)

        return embeddings.embed_query(text)

    def payload(self) -> dict:
        return {
            "collection": "activities",
            "source_id": str(self.activity['_id']),
            "title": self.activity['dn'],
            "ft": "pdf",
        }
