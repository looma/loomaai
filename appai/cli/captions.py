import os

import whisper
from whisper.utils import get_writer
from pymongo.mongo_client import MongoClient
from alive_progress import alive_bar
import requests

def transcribe_one_video(video_url: str, output_dir: str):
    writer = get_writer("vtt", output_dir)

    model = whisper.load_model("small")
    result = model.transcribe(video_url)
    writer(result, video_url)

def transcribe_all_videos():
    data_dir = os.getenv("DATADIR")
    MONGO_URI = os.getenv("MONGO_URI")
    DATABASE_NAME = os.getenv("MONGO_DB")
    client = MongoClient(MONGO_URI)
    db = client.get_database(DATABASE_NAME)
    activities_collection = db.get_collection("activities")
    activities = activities_collection.find({"ft": {"$eq": "video"}})

    output_dir = data_dir+"/content/video_captions/"

    with alive_bar(activities_collection.count_documents({"ft": {"$eq": "video"}})) as progress_bar:
        for activity in activities:
            try:
                fn = activity['fn']
                fp = activity.get('fp', '../content/videos/').removeprefix("..")
                if os.path.exists(output_dir + "en/" + fp+os.path.splitext(fn)[0] + ".vtt"):
                    print(f"SKIPPING {fn}: transcript file exists on disk")

                response = requests.get(f"https://looma.website/{fp}{fn}")
                if response.status_code == 200:
                    download_dir = data_dir+fp
                    os.makedirs(download_dir, exist_ok=True)
                    with open(download_dir+fn, "wb") as f:
                        f.write(response.content)
                    os.makedirs(output_dir+"en"+fp, exist_ok=True)
                    transcribe_one_video(video_url=download_dir+fn, output_dir=output_dir+"en"+fp)
                    print(f"COMPLETED {activity["_id"]} {fn}")
                else:
                    print(f"SKIPPING {fn}: not found on server")

            except Exception as e:
                print(f"ERROR on activity {activity["_id"]}: {e}")
            progress_bar()



transcribe_all_videos()
