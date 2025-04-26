import os

from ..common.translate_lessons import translate_lessons

from pymongo import MongoClient
from langchain_openai import ChatOpenAI
import argparse

MONGO_URI = os.getenv("MONGO_URI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = MongoClient(MONGO_URI)
llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")


parser = argparse.ArgumentParser(description="Translate lessons in the database.")
parser.add_argument("--missing-only", action="store_true", help="Translate only missing lessons.")
args = parser.parse_args()

missing_only = args.missing_only
translate_lessons(db=client.get_database('looma'), llm=llm, missing_only=missing_only)
