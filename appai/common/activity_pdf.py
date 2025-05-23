from langchain_huggingface import HuggingFaceEmbeddings
from pymongo.synchronous.database import Database

from .activity import Activity, download_pdf, extract_text_from_pdf


class PdfActivity(Activity):
    def get_text(self, mongo: Database) -> str:
        fp = self.activity['fp'] if 'fp' in self.activity else '../content/pdfs/'
        url = f"https://looma.website/{fp}{self.activity['fn']}"
        pdf_stream = download_pdf(url)
        return extract_text_from_pdf(pdf_stream)
    
    def embed(self, mongo: Database, embeddings: HuggingFaceEmbeddings) -> list[float]:


        return embeddings.embed_query(self.get_text(mongo))

    def payload(self) -> dict:
        return {
            "collection": "activities",
            "source_id": str(self.activity['_id']),
            "title": self.activity['dn'],
            "ft": "pdf",
        }
