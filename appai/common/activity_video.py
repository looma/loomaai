import os
import re

from .activity import Activity

from langchain_huggingface import HuggingFaceEmbeddings
from pymongo.synchronous.database import Database

class VideoActivity(Activity):
    def en_caption_path(self):
        data_dir = os.getenv("DATADIR")

        fn = self.activity['fn']
        fp = self.activity.get('fp', '../content/videos/').removeprefix("..")
        return data_dir + fp+os.path.splitext(fn)[0] + ".vtt"

    def get_text(self, mongo: Database) -> str:
        timestamp_pattern = re.compile(r'^(\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}\.\d{3})$')
        with open(self.en_caption_path(), "r", encoding="utf-8") as file:
            return " ".join([line for line in file if not timestamp_pattern.match(line.strip())])

    def embed(self, mongo: Database, embeddings: HuggingFaceEmbeddings) -> list[float]:
            return embeddings.embed_query(self.get_text(mongo))

    def payload(self) -> dict:
        return {
            "collection": "activities",
            "source_id": str(self.activity['_id']),
            "title": self.activity['dn'],
            "ft": "video",
        }
