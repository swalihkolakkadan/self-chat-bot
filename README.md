# Swalih Chatbot API

AI-powered chatbot backend that responds as Swalih with voice and lip-sync avatar support.

## Tech Stack

- **FastAPI** - Web framework
- **LangChain** - RAG pipeline
- **Google Gemini** - LLM
- **Chroma** - Vector database
- **ElevenLabs** - Text-to-speech

## Setup

1. Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment:

```bash
cp .env.example .env
# Edit .env with your API keys, GITHUB_TOKEN, and PRIVATE_KNOWLEDGE_REPO
```

4. Fetch knowledge base from private repo:

```bash
python scripts/fetch_private_knowledge.py
```

> Knowledge files are stored in a **private** GitHub repo to keep personal
> documents out of this public repository. See `.env.example` for the
> required environment variables (`GITHUB_TOKEN`, `PRIVATE_KNOWLEDGE_REPO`).

5. Ingest knowledge base:

```bash
python -m app.rag.ingest
```

6. Run the server:

```bash
uvicorn app.main:app --reload
```

## API Endpoints

| Endpoint           | Method | Description              |
| ------------------ | ------ | ------------------------ |
| `/api/health`      | GET    | Health check             |
| `/api/chat`        | POST   | Get complete response    |
| `/api/chat/stream` | POST   | SSE streaming response   |
| `/api/ingest`      | POST   | Re-ingest knowledge base |

## Knowledge Base

Knowledge files are fetched at build time from a **private** GitHub repository.
The `knowledge/` directory is gitignored — files are populated by running
`python scripts/fetch_private_knowledge.py`.

Expected structure (in the private repo):

```
personal/
├── about.md
portfolio/
├── experience.md
├── projects.md
└── skills.md
stories/
└── ...
```

## Deployment

Deploy to Render:

1. Connect GitHub repo
2. Set environment: Python 3.11
3. Build command: `pip install -r requirements.txt && python scripts/fetch_private_knowledge.py && python -m app.rag.ingest`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (including `GITHUB_TOKEN` and `PRIVATE_KNOWLEDGE_REPO`)
