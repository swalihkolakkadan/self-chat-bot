#!/bin/bash
set -e

# Check if knowledge exists (ingested at build time)
if [ ! -d "chroma_db" ] || [ -z "$(ls -A chroma_db)" ]; then
    echo "⚠️  ChromaDB not found or empty. Attempting runtime ingestion (fallback)..."
    
    # Fallback to runtime fetch/ingest if not done at build time
    if [ -n "$GITHUB_TOKEN" ] && [ -n "$PRIVATE_KNOWLEDGE_REPO" ]; then
        echo "Fetching private knowledge..."
        python scripts/fetch_private_knowledge.py
    fi
    
    echo "Ingesting knowledge..."
    python -m app.rag.ingest
else
    echo "✅ Knowledge base found (ingested at build time)."
fi

# Get port from environment variable or default to 8000
PORT="${PORT:-8000}"

# Start the application
echo "Starting application on port $PORT..."
uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
