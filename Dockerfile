FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY pyproject.toml ./
RUN uv sync --no-dev

COPY app ./app
COPY main.py .
COPY README.md .
COPY .env.example .
COPY data ./data

CMD ["uv", "run", "python", "main.py", "--help"]
