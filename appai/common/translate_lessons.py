from pymongo.database import Database
from langchain_openai import ChatOpenAI
from .summary import prompt_text
from bson.objectid import ObjectId
from datetime import datetime

def translate_lessons(db: Database, llm: ChatOpenAI):
    for lesson in db.get_collection("lessons").find({}):
        try:
            translate_one_lesson(db, lesson, llm)
            print(f"Translated lesson {lesson['_id']}")
        except Exception as e:
            print(f"Error translating lesson {lesson['_id']}: {e}")
    print("All lessons have been translated.")


def translate_one_lesson(db: Database, lesson, llm: ChatOpenAI):
    lesson_data: list = lesson["data"]
    for data in lesson_data:
        if data.get("ft") == "inline" and "html" in data:
            translated_html = prompt_text(llm,
                                          "Translate the following html to Nepali, preserving all formatting and html, only translating the visible text. Return only the html with no extra comments: {text}",
                                          data["html"])
            data["nepali"] = translated_html.removeprefix("```").removesuffix("```")
    db.lessons.update_one(
        {"_id": ObjectId(lesson["_id"])},
        {"$set": {"data": lesson_data,"translator":"AI","translated": datetime.now()}}
    )