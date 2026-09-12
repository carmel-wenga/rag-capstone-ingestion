from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    vector_db_url: str = Field(..., alias="VECTOR_DB_URL")
    vector_db_collection: str = Field(..., alias="VECTOR_DB_COLLECTION")
    vector_db_username: str | None = Field(None, alias="VECTOR_DB_USERNAME")
    vector_db_password: str | None = Field(None, alias="VECTOR_DB_PASSWORD")
    vector_db_verify_certs: bool = Field(False, alias="VECTOR_DB_VERIFY_CERTS")

    embedding_model: str = Field("text-embedding-3-small", alias="EMBEDDING_MODEL")
    embedding_dims: int = Field(1536, alias="EMBEDDING_DIMS")
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")

    chunk_size: int = Field(1200, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(200, alias="CHUNK_OVERLAP")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()

