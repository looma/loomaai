import os

from ..common.translate_lessons import translate_lessons
from ..common.llmselect import LLMSelect
from pymongo import MongoClient

import argparse

MONGO_URI = os.getenv("MONGO_URI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = MongoClient(MONGO_URI)
llm = LLMSelect().llm()  # This will use the default LLM selected in LLMSelect


parser = argparse.ArgumentParser(description="Translate lessons in the database.")
parser.add_argument(
    "--missing-only", action="store_true", help="Translate only missing lessons."
)
args = parser.parse_args()

missing_only = args.missing_only
translate_lessons(db=client.get_database("looma"), llm=llm, missing_only=missing_only)
