from __future__ import annotations

from dataclasses import dataclass

from langchain_text_splitters import RecursiveCharacterTextSplitter


@dataclass(frozen=True)
class TextChunk:
    text: str
    chunk_index: int


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[TextChunk]:
    """

    :param text:
    :param chunk_size:
    :param chunk_overlap:
    :return:
    """

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " "],
    )

    chunks = []
    for index, chunk in enumerate(splitter.split_text(text)):
        if chunk.strip():
            chunks.append(TextChunk(text=chunk, chunk_index=index))

    return chunks
