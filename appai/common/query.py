from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
import qdrant_client.models as models

def query(q: str, qdrant: QdrantClient):

    model_name = "sentence-transformers/all-mpnet-base-v2"
    model_kwargs = {}
    encode_kwargs = {'normalize_embeddings': False}
    hf = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    embedded = hf.embed_query(q)
    results = qdrant.search_batch(
        collection_name="activities",
        requests=[
            models.SearchRequest(
                vector=models.NamedVector(
                    name="text-body",
                    vector=embedded,
                ),
                limit=10,
            ),
            models.SearchRequest(
                vector=models.NamedVector(
                    name="text-title",
                    vector=embedded
                ),
                limit=10,
            ),
        ],
    )

    return [*results[0], *results[1]]