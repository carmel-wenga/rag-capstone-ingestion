# rag-capstone-ingestion

Minimal ingestion service for a RAG pipeline. It reads local documents, extracts text, chunks with LangChain, generates embeddings with LangChain, and stores chunks in Elasticsearch.

## Project structure

```text
rag-capstone-ingestion/
  main.py
  app/
    config.py
    ingest.py
    chunking.py
    embeddings.py
    vectordb.py
    schema.py
  data/
  pyproject.toml
  uv.lock
  Dockerfile
  .env.example
  README.md
```

## Requirements

- Docker
- `uv`
- OpenAI API key for embeddings

## Environment variables

Create a `.env` file from `.env.example`:

```env
VECTOR_DB_URL=http://elastic:9200
VECTOR_DB_COLLECTION=rag-documents
VECTOR_DB_VERIFY_CERTS=false
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMS=1536
OPENAI_API_KEY=your-openai-api-key
CHUNK_SIZE=500
CHUNK_OVERLAP=50
```

`VECTOR_DB_URL` should point to Elasticsearch on the shared Docker network.

## Elasticsearch setup

### 1. Create a Docker network

```bash
docker network create rag-network
```

### 2. Start Elasticsearch

```bash
docker run -d \
  --name rag-vector-db \
  --network rag-network \
  -p 9200:9200 \
  -e discovery.type=single-node \
  -e xpack.security.enabled=false \
  -e xpack.security.http.ssl.enabled=false \
  docker.elastic.co/elasticsearch/elasticsearch:9.5.2
```

## Ingestion workflow

The workflow is:

`file -> extract text -> LangChain chunking -> embeddings -> Elasticsearch upsert`

Supported inputs:

- `.pdf`
- `.txt`
- `.md`

`document_id` is derived from a stable hash in the ingestion code, and `chunk_id` is derived from `document_id + page + chunk index`.

## Run the ingestion workflow

### Local run

```bash
uv python install 3.13
uv sync
uv run --python 3.13 python main.py ingest --source ./data
```

Single file:

```bash
uv run --python 3.13 python main.py ingest --source ./data/policies.pdf
```

### Docker run

Build the image:

```bash
docker build -t rag-capstone-ingestion .
```

Run ingestion on the same Docker network:

```bash
docker run --rm \
  --network rag-network \
  --env-file .env \
  -v "$(pwd)/data:/app/data" \
  rag-capstone-ingestion \
  uv run --python 3.13 python main.py ingest --source ./data
```

## Notes

- `uv sync` creates the local `.venv`
- The project uses LangChain for both chunking and embeddings
- The current Elasticsearch client expects the index to exist before ingestion
