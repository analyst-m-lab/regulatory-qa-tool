# Regulatory Q&A Tool

AI-powered Q&A system for pharmaceutical regulatory guidelines (ICH, EMA). Uses BM25 keyword retrieval and Claude (Anthropic) to answer questions grounded in regulatory documents.

## Architecture

```
regulatory-qa-tool/
├── backend/        # FastAPI + BM25 RAG + Claude
├── frontend/       # React + Vite
└── data/           # Regulatory text files (ICH, EMA)
```

## Quick Start

### 1. Configure environment

```bash
cp backend/.env backend/.env.local  # optional
```

Edit `backend/.env`:
```env
ANTHROPIC_API_KEY=sk-ant-api03-...   # Required: your Anthropic API key
DATA_FOLDER=../data                  # Path to regulatory text files
ALLOWED_ORIGINS=http://localhost:5173
```

### 2. Start the backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Server health check |
| `GET` | `/api/status` | RAG initialization status |
| `POST` | `/api/query` | Ask a regulatory question |

### Query request/response

```json
// POST /api/query
{ "question": "What are ICH Q1A stability testing requirements?" }

// Response
{
  "answer": "...",
  "sources": [{ "filename": "ich_q1a_r2.txt", "source": "..." }],
  "success": true
}
```

## Data

The `data/` folder contains regulatory guidelines in `.txt` format:

- **ICH Q series** — Quality guidelines (stability, validation, impurities, etc.)
- **ICH M series** — Multidisciplinary guidelines (CTD, genotoxicity, bioanalytical, etc.)
- **EMA/CHMP** — EMA Committee guidelines (bioequivalence, excipients, stability, etc.)
- **EC regulations** — European Commission directives and regulations

## How It Works

1. On startup, all `.txt` files in `data/` are loaded into memory
2. A **BM25** index is built for keyword-based retrieval (no internet required)
3. When a question is submitted, the top 5 relevant document chunks are retrieved
4. The chunks and question are sent to **Claude** to generate a grounded answer
5. The answer and source filenames are returned to the frontend
