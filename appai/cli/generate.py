from langchain_openai import ChatOpenAI
from pymongo import MongoClient

from appai.common.generate import generate_vectors

llm = ChatOpenAI(temperature=0, model_name="gpt-4o", api_key="TODO")
client = MongoClient("mongodb://localhost:47017/")

generate_vectors(llm=llm, mongo_client=client, data_dir="data/files/chapters")
