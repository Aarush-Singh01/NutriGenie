# Project Architecture Rules (Non-Obvious Only)

This file provides guidance to agents when working with code in this repository.

## Hidden Architectural Constraints

- **Two orchestration modes must stay API-compatible** — `AgentOrchestrator` (local) and watsonx Orchestrate (production) must expose identical interfaces; any new agent must be registered in both paths.
- **Health Advisory Agent is never called standalone** — it is always invoked as a co-reviewer by the Diet Recommendation Agent when `health_conditions` is non-empty, in addition to being reachable directly.
- **Prompts sent to Granite are anonymized** — user PII (name, ID) must not appear in prompts; use profile attributes only (`age`, `sex`, `conditions`, etc.).
- **ChromaDB is local-only for MVP** — it cannot be shared across multiple backend instances; horizontal scaling requires migration to a remote vector DB (IBM watsonx Discovery or Milvus).
- **SQLite has no migration rollback** — use forward-only schema migrations; design models carefully before first run.
- **Frontend and backend are separate deployment units** — frontend goes to IBM Cloud Object Storage / Cloud Foundry staticfile; backend goes to Code Engine. CORS must be configured explicitly in `main.py`.
- **Granite token budget is a hard constraint** — RAG chunks are truncated to fit 3,000-token input; the retriever must trim chunks if necessary before prompt assembly.
- **intent_classifier.py has two modes** — explicit `request_type` field from frontend (preferred) and Granite-based free-text classification (fallback). Plan for both paths when designing the orchestrator.
- **`data/raw/` knowledge base is curated, not full USDA** — only ~500 common foods are included in MVP. Plans involving nutritional lookups for rare/obscure foods must account for the RAG fallback behavior (§15 of blueprint).
