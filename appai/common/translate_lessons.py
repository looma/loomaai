from pymongo.database import Database
from langchain_openai import ChatOpenAI
from ..common.summary import prompt_text

def translate_lessons(db: Database, llm: ChatOpenAI):
    for lesson in db.get_collection("lessons").find({}):
        try:
            lesson_data: list = lesson["data"]
            lesson_data_np: list = []
            for data in lesson_data:
                if data.get("ft") == "inline" and "html" in data:
                    translated_html = prompt_text(llm, "Translate the following html to Nepali, preserving all formatting and html, only translating the visible text. Return only the html with no extra comments: {text}", data["html"])
                    data["html_np"] = translated_html.removeprefix("```").removesuffix("```")
                lesson_data_np.append(data)
            db.lessons.update_one(
                {"_id": lesson["_id"]},
                {"$set": {"data_np": lesson_data_np}}
            )
            print(f"Translated lesson {lesson['_id']}")
        except Exception as e:
            print(f"Error translating lesson {lesson['_id']}: {e}")
    print("All lessons have been translated.")