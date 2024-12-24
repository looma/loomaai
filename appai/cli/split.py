import argparse

from config import ConfigInit
from ..common.split import *
from pymongo import MongoClient

#parses the location parameter from the command into a string
parser = argparse.ArgumentParser(description="Chapter Splitting Tool")
parser.add_argument("datadir", type=str, help="Data Directory")
parser.add_argument("textbook", type=str, help="Textbook to split")
args = parser.parse_args()

#calls the MongoClient and runs the split function in loomaai/appai/common/split.py
#instructions on the README

cfg = ConfigInit()
config = cfg.json()
MONGO_URI = f"mongodb://{config['mongo']['host']}:{config['mongo']['port']}"
client = MongoClient(MONGO_URI)

split(client=client, files_dir=args.datadir, prefixes=[args.textbook])
print("all textbook chapters have their own pdfs")
