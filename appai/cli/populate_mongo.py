from populate_relevant_resources import populate_relevant_resources

from pymongo import MongoClient
from qdrant_client import QdrantClient

client = MongoClient("mongodb://localhost:47017/")

qclient = QdrantClient(url='http://localhost:46333')
populate_relevant_resources(mongo_client=client, vector_db=qclient)
