from ..common.config import ConfigInit
from ..common.populate_relevant_resources import populate_relevant_resources

from pymongo import MongoClient
from qdrant_client import QdrantClient

cfg = ConfigInit()
config = cfg.json()
MONGO_URI = f"mongodb://{config['mongo']['host']}:{config['mongo']['port']}"
QDRANT_URI = f"http://{config['qdrant']['host']}:{config['qdrant']['port']}"
client = MongoClient(MONGO_URI)
qclient = QdrantClient(url=QDRANT_URI)

populate_relevant_resources(db=client.get_database('looma'), vector_db=qclient)
