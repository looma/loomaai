import os

import whisper
from whisper.utils import get_writer
from pymongo.mongo_client import MongoClient
from alive_progress import alive_bar
import requests
from pathlib import Path

def transcribe_one_video(dir: str, fn: str):
    writer = get_writer("vtt", dir)

    model = whisper.load_model("small")
    result = model.transcribe(dir+fn)
    writer(result, dir+fn)

def transcribe_all_videos():
    data_dir = os.getenv("DATADIR")
    MONGO_URI = os.getenv("MONGO_URI")
    DATABASE_NAME = os.getenv("MONGO_DB")
    client = MongoClient(MONGO_URI)
    db = client.get_database(DATABASE_NAME)
    activities_collection = db.get_collection("activities")
    activities = activities_collection.find({"ft": {"$eq": "video"}})

    with alive_bar(activities_collection.count_documents({"ft": {"$eq": "video"}})) as progress_bar:
        for activity in activities:
            try:
                fn = activity['fn']
                fp = activity.get('fp', '../content/videos/').removeprefix("..")
                download_dir = data_dir+fp
                if os.path.exists(os.path.splitext(download_dir+fn)[0]+".vtt"):
                    print(f"SKIPPING {fn}: transcript file exists on disk")
                    continue

                response = requests.get(f"https://looma.website/{fp}{fn}")
                if response.status_code == 200:
                    os.makedirs(download_dir, exist_ok=True)
                    with open(download_dir+fn, "wb") as f:
                        f.write(response.content)
                    # os.makedirs(output_dir+"en"+fp, exist_ok=True)
                    transcribe_one_video(dir=download_dir, fn=fn)
                    print(f"COMPLETED {activity["_id"]} {fn}")
                else:
                    print(f"SKIPPING {fn}: not found on server")

            except Exception as e:
                print(f"ERROR on activity {activity["_id"]}: {e}")
            progress_bar()

transcribe_all_videos()
