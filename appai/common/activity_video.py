import os

from .activity import Activity

from langchain_huggingface import HuggingFaceEmbeddings
from pymongo.synchronous.database import Database

class VideoActivity(Activity):
    def en_caption_path(self):
        data_dir = os.getenv("DATADIR")
        output_dir = data_dir+"/content/video_captions/"

        fn = self.activity['fn']
        fp = self.activity.get('fp', '../content/videos/').removeprefix("..")
        return output_dir + "en" + fp+os.path.splitext(fn)[0] + ".vtt"

    def embed(self, mongo: Database, embeddings: HuggingFaceEmbeddings) -> list[float]:

        with open(self.en_caption_path(), "r", encoding="utf-8") as file:
            return embeddings.embed_query(file.read())

    def payload(self) -> dict:
        return {
            "collection": "activities",
            "source_id": str(self.activity['_id']),
            "title": self.activity['dn'],
            "ft": "video",
        }
