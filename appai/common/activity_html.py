import requests
from bs4 import BeautifulSoup
from langchain_huggingface import HuggingFaceEmbeddings
from pymongo.synchronous.database import Database

from ..common.activity import Activity


class HtmlActivity(Activity):
    def url(self):
        return f"http://looma.website/{self.activity['fp']}{self.activity['fn']}"

    def get_visible_text(self):
        try:
            # Fetch the HTML content from the URL
            response = requests.get(self.url())
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

    def embed(self, mongo: Database, embeddings: HuggingFaceEmbeddings) -> list[float]:

        text = self.get_visible_text()
        return embeddings.embed_query(text)

    def payload(self) -> dict:
        return {
            "collection": "activities",
            "source_id": str(self.activity['_id']),
            "title": self.activity['dn'],
            "ft": "html",
        }
