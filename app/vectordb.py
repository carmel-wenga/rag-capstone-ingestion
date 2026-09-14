from __future__ import annotations

from elasticsearch import Elasticsearch, helpers

from app.config import settings
from app.schema import VectorDocument


def get_elasticsearch_client() -> Elasticsearch:
    return Elasticsearch(settings.vector_db_url)


def create_index(client: Elasticsearch) -> None:
    """
    Create an Elasticsearch index with the specified mappings if it doesn't already exist.
    :param client:
    :return: None
    """
    if client.indices.exists(index=settings.vector_db_collection):
        return

    mappings = {
        "properties": {
            "metadata": {
                "properties": {
                    "chunk_id": {"type": "keyword"},
                    "document_id": {"type": "keyword"},
                    "title": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                    "source": {"type": "keyword"},
                    "page_number": {"type": "integer"},
                    "section": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                    "chunk_index": {"type": "integer"},
                }
            },
            "context": {
                "properties": {
                    "text": {"type": "text"},
                }
            },
            "embedding": {
                "type": "dense_vector",
                "dims": settings.embedding_dims,
                "index": True,
                "similarity": "cosine",
            },
        }
    }
    client.indices.create(index=settings.vector_db_collection, mappings=mappings)


def upsert_documents(client: Elasticsearch, documents: list[VectorDocument]) -> None:
    """
    Upsert a list of VectorDocument instances into the Elasticsearch index.
    :param client: Elasticsearch client instance.
    :param documents: List of VectorDocument instances to upsert.
    :return: None.
    """
    if not documents:
        return

    actions = []

    for document in documents:
        action = {
            "_op_type": "index",
            "_index": settings.vector_db_collection,
            "_id": document.metadata.chunk_id,
            "_source": document.model_dump(),
        }
        actions.append(action)

    helpers.bulk(client, actions)
