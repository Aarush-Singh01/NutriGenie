# Project Coding Rules (Non-Obvious Only)

This file provides guidance to agents when working with code in this repository.

## Implementation Order Matters
Follow the phase order in `PROJECT_BLUEPRINT.md` §19 strictly — later phases depend on earlier ones. Never implement a router before its service, never implement a service before its schema.

## Non-Standard Patterns

- **`AgentOrchestrator` is a drop-in replacement for watsonx Orchestrate** — the routing logic in `backend/orchestration/orchestrator.py` must be structurally identical to what would be configured as Orchestrate Skills, so that swapping to the real API is a single-function change.
- **`backend/agents/base_agent.py`** wires Granite + RAG for all agents — agent subclasses must not import `GraniteClient` or `RAGRetriever` directly; they inherit via the base class.
- **Disclaimer injection in `health_advisory_agent.py`** must be a Python string append *after* the LLM call returns, not inside the prompt — this is a hard safety requirement.
- **`backend/config.py` must use `pydantic-settings` `BaseSettings`** — all env vars declared here; do not use `os.getenv` elsewhere in the codebase.
- **RAG chunk size**: 512 tokens, 50-token overlap — do not change these values without updating the token budget calculation.
- **Granite API endpoint**: `POST /ml/v1/text/generation` at `WATSONX_URL` — the `GraniteClient` uses IAM token exchange, not a static API key header.
- **Frontend is static HTML/JS** — no build step, no bundler. `frontend/app.js` handles tab routing; component files in `frontend/components/` are loaded via `<script>` tags in `index.html`.
- **SQLite file lives inside `backend/`** when `DATABASE_URL=sqlite:///./nutrigenie.db` — the `./` resolves relative to where uvicorn is launched (i.e., `backend/`).
- **`scripts/` run from project root**, not from `backend/` — import paths in scripts must account for this.
