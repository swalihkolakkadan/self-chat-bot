#!/bin/bash
set -e

# Fetch private knowledge if environment variables are set
if [ -n "$GITHUB_TOKEN" ] && [ -n "$PRIVATE_KNOWLEDGE_REPO" ]; then
    echo "Fetching private knowledge..."
    python scripts/fetch_private_knowledge.py
else
    echo "Skipping private knowledge fetch (env vars not set)"
fi

# Ingest knowledge into vector DB
echo "Ingesting knowledge..."
python -m app.rag.ingest

# Get port from environment variable or default to 8000
PORT="${PORT:-8000}"

# Start the application
echo "Starting application on port $PORT..."
uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
