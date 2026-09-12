from langchain_openai import OpenAIEmbeddings

from app.config import settings


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Embed a list of texts using OpenAI embeddings.

    :param texts: List of texts to embed.
    :return: List of embeddings, each corresponding to a text.
    """
    if not texts:
        return []

    client = OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.openai_api_key,
    )
    return client.embed_documents(texts)
