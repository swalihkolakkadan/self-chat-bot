# Swalih Chatbot API

AI-powered chatbot backend that responds as Swalih with voice and lip-sync avatar support.

## Tech Stack

- **FastAPI** - Web framework
- **LangChain** - RAG pipeline
- **Google Gemini** - LLM
- **Chroma** - Vector database
- **Amazon Polly** - Text-to-speech with viseme alignment for lip-sync animation

## Local Development

You can run the backend either natively (faster for dev) or using Docker (better for prod parity).

### Option 1: Native (Recommended for Dev)

1.  **Setup**: Follow steps 1-4 in "Setup" below.
2.  **Run**: `uvicorn app.main:app --reload`
    - _Note_: The first run might be slow as it ingests knowledge. Subsequent runs are fast if `chroma_db` exists.

### Option 2: Docker (Recommended for Verification)

Use this to verify the production build process.

1.  **Build**: You _must_ pass your secrets as build args to populate the knowledge base.
    ```bash
    docker build \
      --build-arg GITHUB_TOKEN=your_token \
      --build-arg PRIVATE_KNOWLEDGE_REPO=owner/repo \
      --build-arg GOOGLE_API_KEY=your_key \
      -t swalih-bot-api .
    ```
2.  **Run**:
    ```bash
    docker run -p 8000:8000 --env-file .env swalih-bot-api
    ```

## Setup (Native)

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
# Edit .env with your API keys, AWS credentials, GITHUB_TOKEN, and PRIVATE_KNOWLEDGE_REPO
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

| Endpoint      | Method | Description              |
| ------------- | ------ | ------------------------ |
| `/api/health` | GET    | Health check             |
| `/api/chat`   | POST   | Get complete response    |
| `/api/ingest` | POST   | Re-ingest knowledge base |

### Chat Response Format

The `/api/chat` endpoint returns:

```json
{
  "text": "Response text...",
  "audio_base64": "base64_encoded_mp3_audio...",
  "alignment": {
    "visemes": [
      { "time": 0.0, "viseme": "p" },
      { "time": 0.05, "viseme": "E" },
      { "time": 0.12, "viseme": "t" }
    ],
    "words": [
      { "time": 0.0, "value": "Hello" },
      { "time": 0.45, "value": "world" }
    ]
  }
}
```

### Viseme Reference

Amazon Polly provides these visemes for lip-sync animation:

| Viseme | Description           | Example Phonemes |
| ------ | --------------------- | ---------------- |
| `p`    | Closed lips           | p, b, m          |
| `t`    | Tongue behind teeth   | t, d, n          |
| `k`    | Back of tongue raised | k, g             |
| `f`    | Lower lip under teeth | f, v             |
| `T`    | Tongue between teeth  | th               |
| `s`    | Teeth together        | s, z             |
| `S`    | Lips rounded          | sh, ch           |
| `r`    | Tongue curled         | r                |
| `a`    | Open mouth            | a                |
| `e`    | Slightly open         | e                |
| `i`    | Wide, closed          | i, ee            |
| `o`    | Rounded, open         | o                |
| `u`    | Rounded, closed       | u, oo            |
| `sil`  | Silence               | (pause)          |

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
