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
    embeddings = hf.embed_query(q)

    similar_docs = qdrant.query_points(
        collection_name="activities",
        prefetch=[
            # models.Prefetch(
            #     query=embeddings,
            #     using="text-title",
            #     limit=12,
            #     # filter=models.Filter(
            #     #     must_not=[
            #     #         models.FieldCondition(key="ft",
            #     #                               match=models.MatchValue(
            #     #                                   value="chapter")),
            #     #     ]
            #     # )
            # ),
            models.Prefetch(
                query=embeddings,  # <-- dense vector
                using="text-body",
                limit=12,
                # filter=models.Filter(
                #     must_not=[
                #         models.FieldCondition(key="ft",
                #                               match=models.MatchValue(
                #                                   value="chapter")),
                #     ]
                # )
            ),
        ],
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        with_payload=True,
    )
    return similar_docs