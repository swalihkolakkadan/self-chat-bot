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
# Edit .env with your API keys
```

4. Add knowledge content:

```bash
# Add markdown files to knowledge/ folder
```

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

Add markdown files to `knowledge/` folder:

```
knowledge/
├── portfolio/
│   ├── experience.md
│   ├── projects.md
│   └── skills.md
├── personal/
│   ├── about.md
│   └── hobbies.md
└── stories/
    └── startup-journey.md
```

## Deployment

Deploy to Render:

1. Connect GitHub repo
2. Set environment: Python 3.11
3. Build command: `pip install -r requirements.txt && python -m app.rag.ingest`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables
