from pymongo import MongoClient
from qdrant_client import QdrantClient

from ..common.config import ConfigInit
from ..common.embed import generate_vectors, create_collection_if_not_exists
#
# parser = argparse.ArgumentParser(description="Embedding tool")
# parser.add_argument("apikey", type=str, help="The OpenAI API key")
# args = parser.parse_args()

# llm = ChatOpenAI(temperature=0, model_name="gpt-4o", api_key="")

cfg = ConfigInit()
config = cfg.json()

MONGO_URI = f"mongodb://{config['mongo']['host']}:{config['mongo']['port']}"
QDRANT_URI = f"http://{config['qdrant']['host']}:{config['qdrant']['port']}"
client = MongoClient(MONGO_URI)
qclient = QdrantClient(url=QDRANT_URI)

qclient.delete_collection("activities")
create_collection_if_not_exists("activities", qclient)
generate_vectors(mongo_client=client, vector_db=qclient)
