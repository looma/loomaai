from langchain_community.embeddings import HuggingFaceEmbeddings
from qdrant_client import QdrantClient

def query(q: str, qdrant: QdrantClient):

    model_name = "sentence-transformers/all-mpnet-base-v2"
    model_kwargs = {}
    encode_kwargs = {'normalize_embeddings': False}
    hf = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )

    docs = qdrant.query_points(collection_name="activities", query=hf.embed_query(q),    with_payload=True,)
    return docs