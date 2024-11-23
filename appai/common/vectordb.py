from openai import models
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore, RetrievalMode
from qdrant_client.http.models import Distance, VectorParams
from common.config import *
from logzero import logger

# The `url` here in the instantiation of the class coule any of the 
# following:
#       VectorStore(":memory")                  - Only in-memory
#       VectorStore("/tmp/langchain-my-qdrant") - persistence in a file
#       VectorStore("servername:6333")          - Use a server for vectors_config
#
class VectorDB:
    def __init__(self, url: str):
        self.qclient = QdrantClient(url)
        # TODO: enable this later
        #self.qclient.set_model(self.qclient.DEFAULT_EMBEDDING_MODEL, providers=["CUDAExecutionProvider", "CPUExecutionProvider"])

    def create_collection(self, collection_name):
        collections = self.qclient.get_collections()
        existing_collections = [collection.name for collection in collections.collections]
        if collection_name in existing_collections:
            logger.info(f"Collection '{collection_name}' already exists.")
        else:
            self.qclient.create_collection(collection_name=collection_name,
                    vectors_config=VectorParams(size=768, distance=Distance.COSINE),
            )
            logger.info(f"Collection '{collection_name}' created.")
    def list_collections(self):
        collections = self.qclient.get_collections()
        return [collection.name for collection in collections.collections]

    def delete_collection(self, collection_name):
        collections = self.qclient.get_collections()
        existing_collections = [collection.name for collection in collections.collections]
        if collection_name in existing_collections:
            self.qclient.delete_collection(collection_name=collection_name)
            logger.info(f"Collection '{collection_name}' deleted.")
        else:
            logger.info(f"Collection '{collection_name}' does not exist.")

    # returns a vector store object with the collection name and embeddings tied to the 
    # collection with the vector store object
    def vector_store(self, collection_name, embeddings, retrieval_mode=RetrievalMode.DENSE):
        vector_store = QdrantVectorStore(client=self.qclient,
                                            collection_name=collection_name,
                                            embedding=embeddings
                                         )
        return vector_store

    def get_collection_points(self, collection_name, point_ids):
        return self.client.retrieve(collection_name=collection_name, ids=point_ids)
    def delete_point(self, collection_name, point_id):
        self.client.delete(
            collection_name=collection_name,
            points_selector=models.PointIdsList(points=[point_id]),
        )

    def scroll_collection_points(self, collection_name, limit=100):
        points = []
        offset = None
        while True:
            response = self.client.scroll(collection_name=collection_name,
                limit=limit, offset=offset, with_payload=True,
                with_vectors=False,
            )
            points.extend(response[0])
            offset = response[1]
            if offset is None:
                break
        return points 

