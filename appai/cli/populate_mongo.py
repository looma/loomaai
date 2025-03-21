import os

from ..common.populate_relevant_resources import populate_relevant_resources

from pymongo import MongoClient
from qdrant_client import QdrantClient

MONGO_URI = os.getenv("MONGO_URI")
QDRANT_URI = os.getenv("QDRANT_URL")
client = MongoClient(MONGO_URI)
qclient = QdrantClient(url=QDRANT_URI)

populate_relevant_resources(db=client.get_database('looma'), vector_db=qclient)
