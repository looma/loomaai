import argparse

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_qdrant import QdrantVectorStore
from pymongo import MongoClient
from qdrant_client import QdrantClient

from ..common.generate import generate_vectors, create_collection_if_not_exists

parser = argparse.ArgumentParser(description="Embedding tool")
parser.add_argument("apikey", type=str, help="The OpenAI API key")
args = parser.parse_args()

llm = ChatOpenAI(temperature=0, model_name="gpt-4o", api_key=args.apikey)
client = MongoClient("mongodb://localhost:47017/")
model_name = "sentence-transformers/all-mpnet-base-v2"
model_kwargs = {}
encode_kwargs = {'normalize_embeddings': False}
hf = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)
qclient = QdrantClient(url='http://localhost:46333')
create_collection_if_not_exists("activities", qclient)
qdrant = QdrantVectorStore.from_existing_collection(embedding=hf,
                                                    collection_name="activities",
                                                    url="http://localhost:46333")
generate_vectors(llm=llm, mongo_client=client, vector_db=qdrant)
