import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
import argparse

from appai.common.split import split
from appai.common.config import *
from pymongo import MongoClient

parser = argparse.ArgumentParser(description="Chapter Splitting Tool")
parser.add_argument("datadir", type=str, help="Data Directory")
args = parser.parse_args()

client = MongoClient("mongodb://localhost:47017/")
split(client=client, files_dir=args.datadir)
print("all textbook chapters have their own pdfs")