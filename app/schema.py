from pydantic import BaseModel, ConfigDict, Field


class ChunkMetadata(BaseModel):
    chunk_id: str
    document_id: str
    title: str
    source: str
    page_number: int
    section: str
    chunk_index: int


class ChunkContext(BaseModel):
    text: str


class VectorDocument(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    metadata: ChunkMetadata
    context: ChunkContext
    embedding: list[float] = Field(..., min_length=1)

