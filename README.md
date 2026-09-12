# rag-capstone-ingestion

Minimal ingestion service for a RAG pipeline. It reads local documents, chunks their text with LangChain, generates embeddings with LangChain, and stores them in Elasticsearch using a single ingestion flow.

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

## Environment variables

Copy `.env.example` to `.env` and fill in the values:

```env
VECTOR_DB_HOST=elasticsearch
VECTOR_DB_PORT=9200
VECTOR_DB_COLLECTION=rag-documents
VECTOR_DB_SCHEME=http
VECTOR_DB_USERNAME=
VECTOR_DB_PASSWORD=
VECTOR_DB_VERIFY_CERTS=false
EMBEDDING_MODEL=text-embedding-3-small
OPENAI_API_KEY=your-openai-api-key
CHUNK_SIZE=1200
CHUNK_OVERLAP=200
```

`VECTOR_DB_HOST` should be the Elasticsearch container name when both containers are attached to the same Docker network.
`EMBEDDING_MODEL` is passed to LangChain's `OpenAIEmbeddings` client.
Chunking uses LangChain's `RecursiveCharacterTextSplitter`.

## Supported inputs

- `.pdf`
- `.docx`
- `.txt`
- `.md`

## Run locally

Create the uv-managed environment:

```bash
uv python install 3.11
uv sync
```

Ingest every supported file under `data/`:

```bash
uv run --python 3.11 python main.py ingest --source ./data
```

Ingest a single file:

```bash
uv run --python 3.11 python main.py ingest --source ./data/policies.pdf
```

## Docker usage

Build the image:

```bash
docker build -t rag-capstone-ingestion .
```

Run it on the same Docker network as Elasticsearch:

```bash
docker run --rm \
  --network shared_network \
  --env-file .env \
  -v "$(pwd)/data:/app/data" \
  rag-capstone-ingestion \
  uv run --python 3.11 python main.py ingest --source ./data
```

`uv sync` creates the local `.venv` and installs locked dependencies for this project. The repository pins uv to Python 3.11 via `.python-version`.

## Elasticsearch document shape

Each indexed document follows this structure:

```json
{
  "metadata": {
    "chunk_id": "pto_policy_2026_p03_c02",
    "document_id": "pto_policy_2026",
    "title": "Paid Time Off Policy",
    "category": "leave",
    "country": "FR",
    "version": "2026.1",
    "effective_date": "2026-01-01",
    "source": "employee_handbook.pdf",
    "page_number": 3,
    "section": "Annual Leave Entitlement",
    "chunk_index": 12
  },
  "context": {
    "text": "Employees are entitled to 25 days of paid annual leave per year..."
  },
  "embedding": [0.0123, -0.0456, 0.0789]
}
```

## Current v1 scope

- One ingestion command
- One backend: Elasticsearch
- Manual execution only
- No manifest or idempotency layer yet
- Tests can be added once the flow stabilizes
