# Project Documentation Rules (Non-Obvious Only)

This file provides guidance to agents when working with code in this repository.

## Codebase Status
**This is a greenfield project.** Only `PROJECT_BLUEPRINT.md` exists. All questions about "how the code works" must be answered from the blueprint — no source files exist yet.

## Counterintuitive Structure
- `backend/` is the Python package root for uvicorn — run `uvicorn main:app` from inside `backend/`, not from project root.
- `data/chroma_db/` is gitignored and auto-generated — it will not exist on a fresh clone.
- The `frontend/` is a static SPA with no build system — "how do I build the frontend?" — you don't; open `index.html` directly or serve with `python -m http.server`.
- `USE_LOCAL_ORCHESTRATOR=true` is the default dev setting — watsonx Orchestrate is only needed for the production deployment path.

## Key Reference Sections in PROJECT_BLUEPRINT.md
- §6: Agent responsibilities and routing logic (essential for understanding multi-agent design)
- §7: RAG pipeline (ingestion vs. query-time behavior)
- §8: Granite prompt template structure (the exact `[SYSTEM]/[CONTEXT]/[USER PROFILE]/[USER REQUEST]/[RESPONSE]` format)
- §12: Full API contract with request/response JSON examples
- §15: Error handling table — defines all fallback behaviors
