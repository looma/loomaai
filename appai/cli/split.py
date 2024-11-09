import argparse

from appai.common.split import split
from pymongo import MongoClient

#parses the location parameter from the command into a string
parser = argparse.ArgumentParser(description="Chapter Splitting Tool")
parser.add_argument("datadir", type=str, help="Data Directory")
parser.add_argument("textbook", type=str, help="Textbook to split")
args = parser.parse_args()

#calls the MongoClient and runs the split function in loomaai/appai/common/split.py
#when running this script, use the command python3 split.py ../../data/files/chapters (prefix of what textbook to split or 'all' for all of them)
client = MongoClient("mongodb://localhost:47017/")
split(client=client, files_dir=args.datadir, textbooks = args.textbook)
print("all textbook chapters have their own pdfs")