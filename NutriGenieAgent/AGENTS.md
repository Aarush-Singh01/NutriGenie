# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Overview
NutriGenie is a **greenfield** AI-powered nutrition agent (AICTE / IBM Bob Hackathon). Only `PROJECT_BLUEPRINT.md` exists; all code must be created from scratch following the blueprint exactly.

## Stack
- **Backend**: Python 3.11, FastAPI, SQLAlchemy, Pydantic v2 (pydantic-settings for config)
- **LLM**: IBM Granite (`ibm/granite-13b-instruct-v2`) via watsonx.ai REST API (`/ml/v1/text/generation`)
- **Orchestration**: IBM watsonx Orchestrate (with local `AgentOrchestrator` fallback)
- **RAG**: ChromaDB (local, file-backed at `data/chroma_db/`) + `sentence-transformers/all-MiniLM-L6-v2` embeddings
- **DB**: SQLite for MVP (`DATABASE_URL=sqlite:///./nutrigenie.db`), IBM Cloudant for production
- **Frontend**: Plain HTML + Tailwind CSS + Vanilla JS + Chart.js (MVP); React is a future enhancement

## Commands (run from `backend/`)
```bash
# Setup
python -m venv venv && venv\Scripts\activate   # Windows
pip install -r requirements.txt

# One-time RAG ingestion (must run before starting backend)
python ../scripts/ingest_knowledge_base.py

# Seed demo data (optional)
python ../scripts/seed_sample_data.py

# Run backend
uvicorn main:app --reload --port 8000

# Run tests
pytest tests/                           # all tests
pytest tests/test_agents.py            # single test file
pytest tests/test_api.py::test_name    # single test

# Serve frontend
python -m http.server 3000             # run from frontend/
```

## Critical Architecture Constraints

1. **`USE_LOCAL_ORCHESTRATOR=true`** env var switches from real watsonx Orchestrate to the local `AgentOrchestrator` — the MVP runs entirely with this flag set.
2. **Disclaimer injection is programmatic**, not LLM-generated — the Health Advisory Agent must append the medical disclaimer in Python code, not inside the prompt, so a model failure cannot omit it.
3. **RAG must run before the backend starts** — `data/chroma_db/` is gitignored and must be populated by `scripts/ingest_knowledge_base.py` on first setup.
4. **Granite prompt structure is fixed** — all agents use the `[SYSTEM] / [CONTEXT] / [USER PROFILE] / [USER REQUEST] / [RESPONSE]` template in `backend/ai/prompt_templates.py`. Max input: 3,000 tokens; max output: 1,000 tokens.
5. **Calorie target uses Mifflin-St Jeor equation** (preferred over Harris-Benedict per blueprint) in `recommendation_agent.py`.
6. **ChromaDB similarity threshold is 0.5** — below this, agents fall back to general knowledge with a disclaimer, not a hard error.
7. **`config.py` uses pydantic-settings**, not plain `os.getenv` — all env vars must be declared in the `Settings` class.
8. **No raw SQL** — all DB access goes through SQLAlchemy ORM + `backend/db/crud.py` helpers.

## Required Environment Variables
```
WATSONX_API_KEY, WATSONX_PROJECT_ID, WATSONX_URL,
WATSONX_ORCHESTRATE_URL, WATSONX_ORCHESTRATE_INSTANCE_ID,
DATABASE_URL, SECRET_KEY, CHROMA_DB_PATH, USE_LOCAL_ORCHESTRATOR
```
Never commit `.env`. Use `.env.example` with placeholder values only.

## Testing Notes
- Granite API calls and ChromaDB are **mocked** in unit tests — full ChromaDB is tested manually only.
- `tests/fixtures/sample_profile.json` is the canonical test profile covering multiple health conditions.
- `test_agents.py` must assert disclaimer presence on every Health Advisory Agent response.
