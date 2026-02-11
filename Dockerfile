FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Build Arguments for Ingestion
ARG GITHUB_TOKEN
ARG PRIVATE_KNOWLEDGE_REPO
ARG GOOGLE_API_KEY
ARG CHROMA_PERSIST_DIR=./chroma_db

# Run ingestion during build if secrets are provided
# We use a single RUN instruction to prevent secrets from persisting in intermediate layers if possible,
# though using secret mounts is better (but more complex for simple Northflank setup).
# We export variables only for this command execution.
RUN if [ -n "$GITHUB_TOKEN" ] && [ -n "$PRIVATE_KNOWLEDGE_REPO" ] && [ -n "$GOOGLE_API_KEY" ]; then \
        echo "Authentication provided. Running build-time ingestion..." && \
        export GITHUB_TOKEN=$GITHUB_TOKEN && \
        export PRIVATE_KNOWLEDGE_REPO=$PRIVATE_KNOWLEDGE_REPO && \
        export GOOGLE_API_KEY=$GOOGLE_API_KEY && \
        python scripts/fetch_private_knowledge.py && \
        python -m app.rag.ingest; \
    else \
        echo "Build arguments not provided. Skipping build-time ingestion."; \
    fi

# Make start script executable
RUN chmod +x start.sh

# Environment variables should be passed at runtime
# Expose the port
EXPOSE 8000

# Run the start script
CMD ["./start.sh"]
