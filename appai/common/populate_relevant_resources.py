import bson
from pymongo.database import Database
from qdrant_client import QdrantClient, models

def populate_resources_for_chapter(vector_db: QdrantClient, mongo_db: Database, chapter: models.Record):
    similar_docs = vector_db.query_points(
        collection_name="activities",
        prefetch=[
            models.Prefetch(
                query=chapter.vector["text-title"],
                using="text-title",
                limit=10,
                filter=models.Filter(
                    must_not=[
                        models.FieldCondition(key="ft",
                                              match=models.MatchValue(
                                                  value="chapter")),
                    ]
                )
            ),
            models.Prefetch(
                query=chapter.vector["text-body"],  # <-- dense vector
                using="text-body",
                limit=10,
                filter=models.Filter(
                    must_not=[
                        models.FieldCondition(key="ft",
                                              match=models.MatchValue(
                                                  value="chapter")),
                    ]
                )
            ),
        ],
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        with_payload=True,
    )

    for activity in similar_docs.points:
        try:
            mongo_db.get_collection("activities").update_one(
                {"_id": bson.ObjectId(activity.payload["source_id"])},
                {"$addToSet": {"ch_id": chapter.payload["chapter_id"]}})
            print(f"Updated relevant resources for chapter {chapter.payload['chapter_id']}")
        except Exception as e:
            print(f"Error updating activity {activity.payload['source_id']}: {e}")

def populate_relevant_resources(db: Database, vector_db: QdrantClient):
    offset = None
    while True:
        (results, offset) = vector_db.scroll(
            collection_name="activities",  # Replace with your collection name
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(key="ft",
                                          match=models.MatchValue(value="chapter")),
                ]
            ),
            limit=10,
            with_vectors=True,
            offset=offset
        )

        for chapter in results:
            try:
                populate_resources_for_chapter(vector_db, db, chapter)
            except Exception as e:
                print(f"Error processing chapter {chapter.payload['chapter_id']}: {e}")

        if offset is None:
            print("Done")
            return