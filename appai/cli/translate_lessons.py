import os

from ..common.translate_lessons import translate_lessons

from pymongo import MongoClient
from langchain_openai import ChatOpenAI

MONGO_URI = os.getenv("MONGO_URI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = MongoClient(MONGO_URI)
llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")

translate_lessons(db=client.get_database('looma'), llm=llm)
