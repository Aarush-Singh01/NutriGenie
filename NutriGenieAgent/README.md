# 🥗 NutriGenie — AI-Powered Personalized Nutrition Agent

> **AICTE / IBM Bob Hackathon Submission**  
> Multi-agent nutrition assistant powered by IBM Granite, watsonx Orchestrate, and RAG.

---

## Problem Statement

Nutrition-related diseases — obesity, diabetes, cardiovascular disease, and micronutrient deficiencies — are among the leading preventable causes of morbidity worldwide. Access to personalized, evidence-based dietary guidance is limited to those who can afford a registered dietitian. Generic dietary apps lack contextual intelligence: they cannot adapt to a user's medical history, cultural background, allergies, or real-time food logs.

## What NutriGenie Does

NutriGenie is an AI-powered multi-agent nutrition assistant that:

- 🎯 Delivers **personalized, context-aware diet plans** using the Mifflin-St Jeor equation
- 📚 **Retrieves grounded nutritional information** from a curated RAG knowledge base (ChromaDB)
- 📝 **Logs food intake** and provides instant nutritional analysis via IBM Granite
- ⚕️ Offers **preventive health guidance** with mandatory medical disclaimers
- 📊 **Visualizes** daily and weekly nutrient intake with Chart.js
- 🤝 Demonstrates **responsible AI**: transparent, grounded, privacy-aware

---

## Architecture

```
Browser (HTML + Tailwind CSS + Vanilla JS + Chart.js)
        │  REST/JSON
        ▼
FastAPI Backend (Python 3.11)
  ├── AgentOrchestrator  ──── classifies intent ──► routes to agent
  │     ├── Nutrition Knowledge Agent
  │     ├── Diet Recommendation Agent
  │     ├── Health Advisory Agent  (disclaimer injected in Python, not LLM)
  │     └── Food Log & Feedback Agent
  │           │
  │           ▼
  │     IBM Granite (ibm/granite-13b-instruct-v2 via watsonx.ai REST)
  │
  ├── RAG Pipeline
  │     ├── ChromaDB (local, file-backed at data/chroma_db/)
  │     └── sentence-transformers/all-MiniLM-L6-v2 embeddings
  │
  └── SQLite DB (SQLAlchemy ORM)
```

### Prompt Structure (fixed for all agents)

```
[SYSTEM]   Agent-specific role + safety instructions
[CONTEXT]  RAG-retrieved knowledge chunks (top-5, similarity ≥ 0.5)
[USER PROFILE]  Age, sex, height, weight, goal, allergies, conditions
[USER REQUEST]  The user's query or task
[RESPONSE]
```

---

## Multi-Agent Design

| Agent | Responsibility |
|---|---|
| **Nutrition Knowledge Agent** | Factual nutrition Q&A grounded in RAG |
| **Diet Recommendation Agent** | Personalized meal plans (Mifflin-St Jeor calorie target) |
| **Health Advisory Agent** | Preventive guidance with mandatory programmatic disclaimer |
| **Food Log & Feedback Agent** | Analyze logged foods, estimate macros, give feedback |

The **AgentOrchestrator** classifies intent via:
1. Explicit `request_type` field from the frontend
2. Keyword-based heuristics as fallback (mirrors watsonx Orchestrate skill routing)

Swapping to real watsonx Orchestrate requires replacing one function in `orchestration/orchestrator.py`.

---

## RAG Design

- **Knowledge base**: `data/nutrition_knowledge.json` (30+ Indian foods with macros/micros) + Markdown guides for diabetes, hypertension, anemia, RDI tables, and Indian food culture
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (local, no API key needed)
- **Chunk size**: 512 tokens (≈2048 chars), 50-token (≈200 char) overlap
- **Retrieval**: Top-5 by cosine similarity; threshold 0.5 (below → general knowledge fallback)
- **Storage**: ChromaDB persistent local store at `data/chroma_db/`

---

## IBM Granite Integration

- **Model**: `ibm/granite-13b-instruct-v2` via `POST /ml/v1/text/generation`
- **Auth**: IBM IAM API key exchange (`WATSONX_API_KEY` env var)
- **Fallback**: When credentials are absent, clearly-labelled `[FALLBACK]` responses with general info
- **Token budget**: 3,000 max input / 1,000 max output
- **Retry**: 2 attempts with 2-second delay on timeout

---

## IBM watsonx Orchestrate Integration

- `USE_LOCAL_ORCHESTRATOR=true` (default) → local `AgentOrchestrator` (no Orchestrate credentials needed)
- `USE_LOCAL_ORCHESTRATOR=false` → calls real watsonx Orchestrate REST API
- Interface is structurally identical — single-function swap to go to production

---

## Setup Instructions

### Prerequisites
- Python 3.11+
- `pip` and `venv`
- Optional: IBM Cloud account with watsonx.ai access

### 1. Clone & Setup

```bash
git clone <repo_url>
cd NutriGenie

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r backend/requirements.txt
```

### 2. Configure Environment Variables

```bash
copy .env.example backend\.env    # Windows
# cp .env.example backend/.env   # macOS/Linux
```

Edit `backend/.env` and add your IBM credentials (or leave as-is to use fallback mode):

```
WATSONX_API_KEY=your_ibm_cloud_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
USE_LOCAL_ORCHESTRATOR=true
```

### 3. Ingest the Knowledge Base (one-time)

```bash
cd backend
python ../scripts/ingest_knowledge_base.py
```

This populates `data/chroma_db/` with the nutrition knowledge vectors.

### 4. Seed Demo Data (optional)

```bash
python ../scripts/seed_sample_data.py
```

This creates a demo user profile and 7 days of sample food logs.

### 5. Start the Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

API is available at `http://localhost:8000`  
Interactive docs: `http://localhost:8000/docs`

### 6. Start the Frontend

```bash
cd frontend
python -m http.server 3000
```

Open `http://localhost:3000` in your browser.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `WATSONX_API_KEY` | For real AI | IBM Cloud API key for watsonx.ai |
| `WATSONX_PROJECT_ID` | For real AI | watsonx.ai project ID |
| `WATSONX_URL` | For real AI | watsonx.ai endpoint URL |
| `WATSONX_MODEL_ID` | Optional | Defaults to `ibm/granite-13b-instruct-v2` |
| `WATSONX_ORCHESTRATE_URL` | Production | watsonx Orchestrate URL |
| `WATSONX_ORCHESTRATE_INSTANCE_ID` | Production | Orchestrate instance ID |
| `USE_LOCAL_ORCHESTRATOR` | No | `true` (default) uses local router |
| `DATABASE_URL` | No | Defaults to `sqlite:///./nutrigenie.db` |
| `CHROMA_DB_PATH` | No | Defaults to `../data/chroma_db` |
| `SECRET_KEY` | No | FastAPI session secret |

---

## How to Run Tests

```bash
cd backend
pytest ../tests/ -v
```

### Test Coverage
- `test_api.py` — FastAPI integration tests (health, profile, log, dashboard, chat)
- `test_agents.py` — Agent unit tests with mocked Granite/RAG; disclaimer presence assertions

---

## Example Demo Prompts

| Prompt | Route |
|---|---|
| `How many calories in 100g of brown rice?` | Nutrition Knowledge Agent |
| `Generate a vegetarian 1-day meal plan for weight loss` | Diet Recommendation Agent |
| `What should I eat if I have diabetes and hypertension?` | Health Advisory Agent |
| `I ate 150g toor dal for lunch` | Food Log & Feedback Agent |
| `Which Indian foods are high in iron?` | Nutrition Knowledge Agent |
| `Create a high-protein meal plan for muscle gain` | Diet Recommendation Agent |
| `Tips for managing blood pressure through diet` | Health Advisory Agent |

---

## Project Structure

```
NutriGenie/
├── backend/
│   ├── main.py               # FastAPI app entry point
│   ├── config.py             # pydantic-settings configuration
│   ├── agents/               # 4 specialized agents + base class
│   ├── ai/                   # Granite client + prompt templates
│   ├── db/                   # SQLAlchemy models, CRUD, session
│   ├── orchestration/        # AgentOrchestrator + intent classifier
│   ├── rag/                  # ChromaDB client, retriever, ingestor
│   ├── routers/              # FastAPI route handlers
│   ├── schemas/              # Pydantic request/response models
│   ├── services/             # Business logic layer
│   └── requirements.txt
├── data/
│   ├── nutrition_knowledge.json     # 30+ foods with macros/micros
│   └── raw/                         # Markdown guidance docs
├── frontend/
│   ├── index.html            # Single-page app shell
│   ├── app.js                # Tab routing + API utilities
│   ├── style.css             # Custom styles
│   └── components/           # Profile, Dashboard, MealPlan, FoodLog, Chat
├── scripts/
│   ├── ingest_knowledge_base.py
│   └── seed_sample_data.py
├── tests/
│   ├── test_api.py
│   ├── test_agents.py
│   └── fixtures/sample_profile.json
├── .env.example
└── README.md
```

---

## Limitations (MVP)

- **IBM Granite responses**: Without valid IBM credentials, all AI responses are fallback (general info). Add real credentials for full AI responses.
- **Nutritional values**: Estimated from knowledge base; not a clinical nutrition database.
- **No authentication**: MVP uses a simple user_id string. Add IBM App ID for production.
- **Single user**: MVP is designed for single-user demo. Cloudant + Auth needed for multi-user.
- **RAG knowledge base**: ~30 foods + 4 guidance documents. Production needs USDA FoodData Central integration.

---

## Future Scope

| Enhancement | Description |
|---|---|
| Barcode/Photo logging | Scan product barcodes or take meal photos |
| Wearable integration | Sync with Fitbit / Apple Health |
| Multilingual support | Hindi, Tamil, Telugu via Granite multilingual |
| IBM Cloudant | Multi-user production database |
| USDA FoodData Central | Full 350,000 food dataset ingestion |
| Fine-tuned Granite | Domain-specific nutrition fine-tuning |
| Real-time alerts | Push notifications for nutrient deficiencies |
| React frontend | Progressive upgrade from HTML + Tailwind |

---

*NutriGenie — AICTE / IBM Bob Hackathon | Blueprint v1.0 | MVP-first, production-ready architecture*
