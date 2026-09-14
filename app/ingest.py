from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from app.chunking import chunk_text
from app.config import settings
from app.embeddings import embed_texts
from app.schema import ChunkContext, ChunkMetadata, VectorDocument
from app.vectordb import create_index, get_elasticsearch_client, upsert_documents

from slugify import slugify

import hashlib

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


def run_ingestion(source_dir: str) -> None:
    """
    Ingests documents from the specified source path, processes them into chunks, generates embeddings, and
    upserts them into an Elasticsearch index.

    :param source_dir: Path to the source directory containing documents to ingest.
    :return: None
    """

    # 1. List all the files in the source dir
    source = Path(source_dir)
    file_paths = []
    if source.is_dir():
        sub_paths = source.rglob("*")
        for path in sub_paths:
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
                file_paths.append(path)
    else:
        raise ValueError(f"Source path {source_dir} is not a directory or does not exist.")

    # 2. Process each file: Extract sections, chunk text, generate embeddings, and prepare documents for ingestion.
    documents: list[VectorDocument] = []
    for file_path in file_paths:
        # 2.1. Extract document content or sections
        document_id = f"{slugify(file_path.stem)}-{hashlib.sha256(file_path.read_bytes()).hexdigest()}"
        document_title = _generate_title(file_path.stem)
        raw_sections = _extract_sections(file_path)
        print(f"Processing File: {file_path} - {len(raw_sections)} pages.")

        nb_chunks = 0
        # 2.2. Chunk All Documents
        for page_number, section_name, text in raw_sections:
            chunks = chunk_text(
                text=text,
                chunk_size=settings.chunk_size,
                chunk_overlap=settings.chunk_overlap,
            )

            # 2.3. Generate Embeddings for all chunks if "chunks" is not empty
            if chunks:
                nb_chunks += len(chunks)
                embeddings = embed_texts([chunk.text for chunk in chunks])

                for chunk, embedding in zip(chunks, embeddings, strict=True):
                    metadata = ChunkMetadata(
                        chunk_id=f"{document_id}_p{page_number:02d}_c{chunk.chunk_index:03d}",
                        document_id=document_id,
                        title=document_title,
                        source=file_path.name,
                        page_number=page_number,
                        section=section_name,
                        chunk_index=chunk.chunk_index,
                    )
                    documents.append(
                        VectorDocument(
                            metadata=metadata,
                            context=ChunkContext(text=chunk.text),
                            embedding=embedding,
                        )
                    )
        print(
            f"Processed File: {file_path} - {len(raw_sections)} pages - "
            f"Generated {nb_chunks} chunks and embeddings."
        )

    # 3. Create or update Elasticsearch index: Ingest document into Elasticsearch.
    if documents:
        elasticsearch_client = get_elasticsearch_client()
        create_index(elasticsearch_client)
        upsert_documents(elasticsearch_client, documents)


def _extract_sections(file_path: Path) -> list[tuple[int, str, str]]:
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf_sections(file_path)
    return [(1, "Full Document", file_path.read_text(encoding="utf-8"))]


def _extract_pdf_sections(file_path: Path) -> list[tuple[int, str, str]]:
    """
    Extracts content from a PDF file.

    :param file_path: Path to the PDF file.
    :return: A list of tuples containing page number, section title, and text. Example:
        [
            (1, "Page 1", "Text of page 1..."),
            (2, "Page 2", "Text of page 2..."),
            ...
        ]
    """
    reader = PdfReader(str(file_path))
    sections: list[tuple[int, str, str]] = []
    for index, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            sections.append((index, f"Page {index}", text))
    return sections


def _generate_title(stem: str) -> str:
    """
    This function generates a human-readable title from a file stem by replacing underscores and hyphens with spaces,
    stripping leading/trailing whitespace, and converting the string to title case.
    Example: "hr_policies_document" will return "Hr Policies Document"

    :param stem: The file stem (base name without extension).
    :return: A human-readable title.
    """
    return stem.replace("_", " ").replace("-", " ").strip().title()

