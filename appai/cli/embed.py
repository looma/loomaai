import argparse

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_qdrant import QdrantVectorStore
from pymongo import MongoClient
from qdrant_client import QdrantClient

from ..common.embed import generate_vectors, create_collection_if_not_exists
#
# parser = argparse.ArgumentParser(description="Embedding tool")
# parser.add_argument("apikey", type=str, help="The OpenAI API key")
# args = parser.parse_args()

# llm = ChatOpenAI(temperature=0, model_name="gpt-4o", api_key="")
client = MongoClient("mongodb://localhost:47017/")

qclient = QdrantClient(url='http://localhost:46333')
qclient.delete_collection("activities")
create_collection_if_not_exists("activities", qclient)
generate_vectors(mongo_client=client, vector_db=qclient)
