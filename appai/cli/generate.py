import argparse

from langchain_openai import ChatOpenAI
from pymongo import MongoClient

from ..common.generate import generate_vectors
parser = argparse.ArgumentParser(description="Embedding tool")
parser.add_argument("apikey", type=str, help="The OpenAI API key")
args = parser.parse_args()

llm = ChatOpenAI(temperature=0, model_name="gpt-4o", api_key=args.apikey)
client = MongoClient("mongodb://localhost:47017/")
generate_vectors(llm=llm, mongo_client=client, data_dir="data/files/chapters")
