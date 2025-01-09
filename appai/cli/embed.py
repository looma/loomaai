from pymongo import MongoClient
from qdrant_client import QdrantClient

from ..common.embed import generate_vectors, create_collection_if_not_exists
import argparse

parser = argparse.ArgumentParser(description="Embed all activities or only missing activities")
parser.add_argument("--missing-only", action="store_true", help="Only embed activities that are not already embedded in qdrant. Requires the collection \"activities\" to already exist in qdrant")

args = parser.parse_args()

client = MongoClient("localhost:47017")
qclient = QdrantClient(url="localhost:46333")


if not args.missing_only:
    qclient.delete_collection("activities")
    create_collection_if_not_exists("activities", qclient)
    print("Deleted and created fresh activities collection in qdrant")
else:
    print("Only embedding missing activities")

generate_vectors(mongo_client=client, vector_db=qclient, missing_only=True)
