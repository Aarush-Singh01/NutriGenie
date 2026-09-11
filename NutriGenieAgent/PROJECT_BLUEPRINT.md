# NutriGenie – AI-Powered Personalized Nutrition Agent
## Project Blueprint v1.0

---

## Table of Contents

1. [Problem Statement and Project Goal](#1-problem-statement-and-project-goal)
2. [User Personas and Key Use Cases](#2-user-personas-and-key-use-cases)
3. [Functional Requirements](#3-functional-requirements)
4. [Non-Functional Requirements](#4-non-functional-requirements)
5. [Complete System Architecture](#5-complete-system-architecture)
6. [Multi-Agent Architecture and Responsibilities](#6-multi-agent-architecture-and-responsibilities)
7. [RAG Architecture and Data Flow](#7-rag-architecture-and-data-flow)
8. [IBM Granite Integration](#8-ibm-granite-integration)
9. [IBM watsonx Orchestrate Integration](#9-ibm-watsonx-orchestrate-integration)
10. [Frontend / Backend Architecture](#10-frontend--backend-architecture)
11. [End-to-End Request / Data Flow](#11-end-to-end-request--data-flow)
12. [API Endpoints](#12-api-endpoints)
13. [Project File / Folder Structure](#13-project-file--folder-structure)
14. [Security and Privacy Considerations](#14-security-and-privacy-considerations)
15. [Error Handling and Fallback Behavior](#15-error-handling-and-fallback-behavior)
16. [Testing Strategy](#16-testing-strategy)
17. [Local Development and Deployment](#17-local-development-and-deployment)
18. [Future Scalability and Enhancements](#18-future-scalability-and-enhancements)
19. [Step-by-Step Implementation Order](#19-step-by-step-implementation-order)

---

## 1. Problem Statement and Project Goal

### Problem Statement
Nutrition-related diseases — obesity, diabetes, cardiovascular disease, and micronutrient deficiencies — are among the leading preventable causes of morbidity worldwide. Access to personalized, evidence-based dietary guidance has historically been limited to those who can afford a registered dietitian. Generic dietary apps lack contextual intelligence: they cannot adapt to a user's medical history, cultural background, allergies, or real-time food logs.

### Project Goal
Build **NutriGenie**, an AI-powered multi-agent nutrition assistant that:
- Delivers personalized, context-aware diet plans.
- Retrieves grounded nutritional information from a curated knowledge base (RAG).
- Logs food intake and provides instant nutritional analysis.
- Offers preventive-health guidance with explicit medical disclaimers.
- Visualizes daily and weekly nutrient intake, deficiencies, and progress.
- Demonstrates responsible AI: transparent, grounded in facts, privacy-aware, and never replacing a medical professional.

### Hackathon Alignment
This project addresses the **Nutrition Agent** problem statement within the AICTE / IBM Bob hackathon track. It leverages IBM Granite (generative/reasoning), IBM watsonx Orchestrate (multi-agent orchestration), and IBM Cloud (infrastructure/deployment).

---

## 2. User Personas and Key Use Cases

### Persona A — Health-Conscious Young Adult (Priya, 24)
- Goal: Lose 5 kg, follow a vegetarian diet, avoid gluten.
- Uses NutriGenie to get a weekly meal plan and log daily meals.
- Needs culturally appropriate Indian vegetarian recipes.

### Persona B — Middle-Aged Adult Managing a Chronic Condition (Ramesh, 48)
- Goal: Manage Type-2 diabetes through diet.
- Needs low-GI meal suggestions and guidance on carbohydrate portions.
- Wants nutritional analysis of foods he already eats.

### Persona C — Fitness Enthusiast (Arjun, 30)
- Goal: Build lean muscle mass.
- Needs high-protein meal plans aligned with workout schedule.
- Tracks macros daily.

### Persona D — Parent (Meena, 38)
- Goal: Plan balanced meals for her family including a lactose-intolerant child.
- Needs allergy-safe recipes and child-appropriate nutritional guidance.

### Key Use Cases

| ID | Use Case |
|----|----------|
| UC-1 | User registers and provides profile: age, weight, height, health conditions, allergies, cultural/dietary preferences, fitness goals. |
| UC-2 | User requests a personalized daily or weekly meal plan. |
| UC-3 | User logs a meal (text or food name) and receives instant nutritional analysis. |
| UC-4 | User asks a nutrition question ("How much protein should I eat?"). |
| UC-5 | User views dashboard: daily calorie progress, macro breakdown, deficiency alerts. |
| UC-6 | User views weekly summary: trend charts, goal progress, recommendations. |
| UC-7 | System proactively suggests corrections based on logged patterns. |

---

## 3. Functional Requirements

### FR-1: User Profile Management
- Collect and persist: age, sex, weight, height, health conditions (diabetes, hypertension, etc.), allergies (nuts, gluten, lactose, etc.), dietary preferences (vegetarian, vegan, halal, etc.), cultural background, and fitness goals.
- Profile used as context in every downstream agent call.

### FR-2: Personalized Diet Plan Generation
- Generate single-day and 7-day meal plans tailored to the user profile.
- Plans include meal names, portions, calorie estimates, and macro breakdown.
- Plans respect allergies, dietary restrictions, and cultural preferences.

### FR-3: RAG-Based Nutritional Information Retrieval
- Retrieve accurate nutritional data (calories, macros, vitamins, minerals) for foods.
- Use a curated local knowledge base for MVP; architecture allows swap to a vector DB.
- Ground all AI responses in retrieved facts; do not hallucinate nutritional values.

### FR-4: Food Logging and Nutritional Analysis
- Allow users to log meals by entering food names and portions.
- Instantly compute: calories, protein, carbohydrates, fat, fiber, key vitamins/minerals.
- Accumulate daily totals and compare against recommended daily intake (RDI) targets.

### FR-5: Preventive Health Guidance
- Provide evidence-based preventive guidance (e.g., "increase fiber to reduce cardiovascular risk").
- Every health-related response must include a visible safety disclaimer: "This is not medical advice. Consult a registered dietitian or physician for personalized medical guidance."
- Never diagnose conditions; never recommend specific medications.

### FR-6: Multi-Agent Orchestration
- Route user requests to the appropriate specialized agent via watsonx Orchestrate.
- Agents collaborate where needed (e.g., diet plan generation requires both the Knowledge Agent and Recommendation Agent).

### FR-7: Visualization Dashboard
- Daily view: calorie ring, macro pie chart, per-nutrient progress bars.
- Weekly view: calorie trend line chart, goal progress, highlighted deficiencies.
- Deficiency alerts: if a nutrient is below 70% of RDI for 3+ consecutive days.

### FR-8: Conversational Interface
- Natural-language chat interface for questions, logging, and advice.
- Maintains session-level conversation history for contextual follow-up.

---

## 4. Non-Functional Requirements

| Category | Requirement |
|----------|-------------|
| **Performance** | API responses within 5 seconds for chat; dashboard renders within 2 seconds from cached data. |
| **Reliability** | Graceful degradation if IBM Cloud / watsonx API is unavailable (cached responses, informative error messages). |
| **Security** | All credentials via environment variables; no secrets in source code; HTTPS in production. |
| **Privacy** | User health data stored locally for MVP; no PII sent to third-party services beyond IBM Cloud. |
| **Usability** | Responsive UI that works on desktop and mobile browsers. |
| **Maintainability** | Clear module boundaries (frontend / backend / agents / RAG / data); documented code. |
| **Portability** | Runs locally via Python (venv) and is deployable to IBM Cloud Foundry or Code Engine. |
| **Disclaimer Compliance** | Medical safety disclaimer always visible on health advisory responses. |

---

## 5. Complete System Architecture

### Layers

```
+--------------------------------------------------------------+
|                     User (Browser)                           |
|              React / HTML+JS  Frontend                       |
+-------------------------------+------------------------------+
                                |  REST / JSON
+-------------------------------v------------------------------+
|                  FastAPI  Backend  (Python)                  |
|  - Session management                                        |
|  - User profile storage (SQLite for MVP)                     |
|  - Food log storage                                          |
|  - Orchestration gateway (calls watsonx Orchestrate)         |
|  - RAG pipeline (local vector store for MVP)                 |
+----------+-------------------+-------------------+----------+
           |                   |                   |
           v                   v                   v
  +--------+------+   +--------+------+   +--------+------+
  | Nutrition     |   | Diet Rec.     |   | Health        |
  | Knowledge     |   | Agent         |   | Advisory      |
  | Agent         |   | (watsonx      |   | Agent         |
  | (watsonx Orch)|   |  Orchestrate) |   | (watsonx Orch)|
  +--------+------+   +--------+------+   +--------+------+
           |                   |                   |
           +-------------------+-------------------+
                               |
                    +----------v----------+
                    | Food Log & Feedback |
                    | Agent               |
                    | (watsonx Orchestrate)|
                    +----------+----------+
                               |
                    +----------v----------+
                    |  IBM Granite LLM    |
                    |  (via watsonx.ai)   |
                    +---------------------+

  +-----------+      +---------------------+
  | RAG Store |      | Nutrition Knowledge |
  | (ChromaDB |<---->| Base (JSON/CSV)     |
  |  local    |      | USDA data + curated |
  |  MVP)     |      | food facts          |
  +-----------+      +---------------------+

  +---------------------------------------------------+
  |           IBM Cloud (Production Deployment)        |
  |  Code Engine / Cloud Foundry + IBM Cloudant (DB)  |
  +---------------------------------------------------+
```

### Key Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React (MVP: plain HTML + Tailwind CSS) |
| Backend API | Python 3.11 + FastAPI |
| LLM | IBM Granite via watsonx.ai API |
| Orchestration | IBM watsonx Orchestrate |
| RAG Vector Store | ChromaDB (local, file-backed) for MVP |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (local, free) |
| Knowledge Base | USDA FoodData Central export (JSON/CSV) + curated nutrition facts |
| User/Food DB | SQLite (MVP) → IBM Cloudant (production) |
| Deployment | IBM Cloud Code Engine (container) |
| Config | python-dotenv + environment variables |

---

## 6. Multi-Agent Architecture and Responsibilities

### Orchestration Model
IBM watsonx Orchestrate acts as the **router and coordinator**. The FastAPI backend sends a structured request to the Orchestrate API endpoint, which dispatches it to the appropriate agent tool/skill. Agents call IBM Granite for generation and the RAG pipeline for grounding.

### Agent Definitions

#### Agent 1 — Nutrition Knowledge Agent
- **Responsibility**: Answer factual nutrition questions. "How many calories are in 100g of brown rice?" "What vitamins are in spinach?"
- **Inputs**: User query, optional food item name, optional quantity.
- **Process**: Run RAG retrieval against the nutrition knowledge base → Granite generates a grounded answer.
- **Outputs**: Structured nutritional fact response with source attribution.
- **Safety**: Does not make health claims; only reports nutritional data.

#### Agent 2 — Diet Recommendation Agent
- **Responsibility**: Generate personalized meal plans.
- **Inputs**: Full user profile (age, weight, health conditions, allergies, goals), requested plan duration (1-day / 7-day), calorie target.
- **Process**: Compute calorie and macro targets from profile → RAG retrieval for suitable foods → Granite generates a structured meal plan respecting all constraints.
- **Outputs**: Structured meal plan (JSON): meals × days, with portions, calories, macros per meal.
- **Safety**: Flags any medical conditions to the Health Advisory Agent for co-review.

#### Agent 3 — Health Advisory Agent
- **Responsibility**: Provide preventive health and nutrition guidance aligned to health conditions.
- **Inputs**: User profile (health conditions), recent food logs (from Food Log Agent), specific health concern.
- **Process**: RAG retrieval for condition-specific nutritional guidance → Granite generates advice with explicit caveats.
- **Outputs**: Advisory text with mandatory medical disclaimer appended to every response.
- **Safety**: Hardcoded disclaimer injection; agent prompt includes strict instructions to never diagnose or prescribe.

#### Agent 4 — Food Log & Feedback Agent
- **Responsibility**: Accept food log entries, compute nutritional totals, compare to targets, and generate feedback.
- **Inputs**: Logged food items + portions, user's daily targets.
- **Process**: RAG lookup for each food item's nutritional data → Accumulate totals → Compare to RDI targets → Granite generates a short feedback/coaching message.
- **Outputs**: Structured log entry (calories, macros, micros), daily totals, target comparison, feedback message.
- **Safety**: Feedback is motivational and factual; no diagnostic language.

### Agent Routing Logic

```
User Request
     |
     +--[nutrition question]---------> Nutrition Knowledge Agent
     |
     +--[meal plan request]----------> Diet Recommendation Agent
     |                                        |
     |                                        +--> Health Advisory Agent
     |                                             (if health conditions present)
     +--[food log entry]-------------> Food Log & Feedback Agent
     |
     +--[health / condition advice]--> Health Advisory Agent
     |
     +--[dashboard data request]-----> Food Log & Feedback Agent
                                       (aggregates stored logs)
```

---

## 7. RAG Architecture and Data Flow

### Knowledge Base Sources (MVP)
1. **USDA FoodData Central** — Publicly available CSV/JSON export. Contains ~350,000 food items with calories, macros, and micronutrients. For MVP, use a curated subset of ~500 common foods.
2. **Curated Nutrition Facts Documents** — Hand-authored Markdown/text files covering:
   - RDI tables (age/sex-specific).
   - Condition-specific guidance (diabetes, hypertension, anemia, lactose intolerance).
   - Allergy substitution lists.
   - Cultural food lists (Indian, Mediterranean, East Asian common foods).

### RAG Pipeline

```
Ingestion (run once / on update):
  Raw data files (CSV, JSON, Markdown)
       |
       v
  Text chunking (chunk size 512 tokens, 50-token overlap)
       |
       v
  Embeddings via sentence-transformers/all-MiniLM-L6-v2
       |
       v
  ChromaDB local collection (persisted to data/chroma_db/)

Query (runtime, per agent call):
  User query / food item name
       |
       v
  Embed query
       |
       v
  ChromaDB similarity search (top-k = 5)
       |
       v
  Retrieved chunks assembled into context string
       |
       v
  Injected into Granite prompt as [CONTEXT] section
       |
       v
  Granite generates grounded response
```

### Fallback
If ChromaDB retrieval returns no results above similarity threshold (0.5):
- Return a structured "no data found" message.
- Granite falls back to general nutritional knowledge with a disclaimer that the information is general and not specific to a logged food item.

---

## 8. IBM Granite Integration

### Model Selection
- **Primary Model**: `ibm/granite-13b-instruct-v2` via IBM watsonx.ai API.
- Granite is chosen for: instruction-following, factual grounding, safety alignment, and IBM ecosystem integration.

### Integration Pattern
- All agent logic calls the watsonx.ai REST API (`/ml/v1/text/generation`).
- Authentication: IBM Cloud IAM API Key (environment variable `WATSONX_API_KEY`) + Project ID (`WATSONX_PROJECT_ID`).
- A shared `GraniteClient` class in `backend/ai/granite_client.py` handles all API calls with retry logic and timeout handling.

### Prompt Engineering Strategy

Each agent uses a structured prompt template:
```
[SYSTEM]
You are a specialized nutrition assistant. <agent-specific role>.
Always ground your answer in the provided context.
Never diagnose medical conditions. Never recommend medications.
<health-advisory-agent only: Always append the disclaimer...>

[CONTEXT]
{rag_retrieved_chunks}

[USER PROFILE]
Age: {age}, Sex: {sex}, Health conditions: {conditions},
Allergies: {allergies}, Dietary preference: {preference},
Goal: {goal}

[USER REQUEST]
{user_query}

[RESPONSE]
```

### Token Budget
- Max input context: 3,000 tokens (system + context + profile + query).
- Max output: 1,000 tokens.
- RAG chunks are truncated to fit within the context budget.

---

## 9. IBM watsonx Orchestrate Integration

### Role in the System
watsonx Orchestrate is used as the **multi-agent orchestration layer**. It exposes the four specialized agents as **Skills** and the backend calls the Orchestrate API to dispatch requests.

### Integration Approach (MVP-Compatible)

Since full watsonx Orchestrate SaaS access may require enterprise provisioning, the MVP uses a **hybrid approach**:
- **Production path**: FastAPI backend calls the watsonx Orchestrate REST API, which routes to the appropriate agent skill.
- **MVP local fallback**: A local `AgentOrchestrator` class in `backend/orchestration/orchestrator.py` mimics the routing logic. It classifies the user intent and dispatches to the appropriate agent module directly. This allows full MVP functionality without a live Orchestrate instance.

The `AgentOrchestrator` is designed so that the routing logic is identical to what would be configured in watsonx Orchestrate; replacing the local dispatcher with the real API call is a single-function swap.

### Intent Classification
The orchestrator determines agent routing via:
1. Explicit request type field from the frontend (`request_type: "meal_plan" | "food_log" | "nutrition_query" | "health_advice" | "dashboard"`).
2. As a fallback: Granite classifies free-text input into one of the above types.

---

## 10. Frontend / Backend Architecture

### Frontend (MVP: Single-Page HTML + Tailwind CSS + Vanilla JS)

Pages / Sections:
1. **Onboarding / Profile Page** — Form to enter user profile. Saved via `POST /api/profile`.
2. **Chat Interface** — A chat panel for natural-language interaction with NutriGenie. Calls `POST /api/chat`.
3. **Food Log Tab** — Form to log a meal (food name + portion). Calls `POST /api/log`. Displays today's accumulated log below.
4. **Meal Plan Tab** — Button to generate a 1-day or 7-day plan. Displays a structured meal card layout. Calls `POST /api/meal-plan`.
5. **Dashboard Tab** — Calorie ring (Chart.js donut), macro pie chart, per-nutrient progress bars, weekly calorie trend line. Data from `GET /api/dashboard`.

### Progressive Enhancement Path
For hackathon submission, the frontend can optionally be built in React (Create React App or Vite) where each tab above becomes a component. The MVP HTML version is sufficient for demonstration.

### Backend (FastAPI, Python 3.11)

Modules:
- `main.py` — FastAPI app entry point, CORS, router registration.
- `routers/` — One router file per feature area (profile, chat, log, meal_plan, dashboard).
- `services/` — Business logic layer (profile service, log service, meal plan service, dashboard service).
- `orchestration/` — AgentOrchestrator, agent dispatch.
- `agents/` — One module per agent (knowledge, recommendation, health_advisory, food_log).
- `ai/` — GraniteClient, prompt templates.
- `rag/` — Ingestor, retriever, ChromaDB client.
- `db/` — SQLite models and session management (SQLAlchemy).
- `schemas/` — Pydantic request/response models.
- `config.py` — Settings loaded from environment variables.

---

## 11. End-to-End Request / Data Flow

### Example: User logs a meal "200g grilled chicken"

```
1. User types "200g grilled chicken" in Food Log tab → clicks Log
2. Frontend POST /api/log  { "food": "grilled chicken", "quantity": 200, "unit": "g" }
3. FastAPI router → LogService.create_entry()
4. LogService → AgentOrchestrator.dispatch(request_type="food_log", payload)
5. AgentOrchestrator → FoodLogAgent.analyze(food, quantity)
6. FoodLogAgent → RAGRetriever.query("grilled chicken nutritional info")
7. ChromaDB → returns top-5 chunks (chicken breast data from USDA)
8. FoodLogAgent → GraniteClient.generate(prompt with RAG context, user profile)
9. Granite returns: {"calories": 330, "protein": 62, "carbs": 0, "fat": 7, ...}
10. FoodLogAgent → structured LogEntry created, saved to SQLite
11. LogService → returns daily totals + feedback message
12. Frontend updates food log table, daily calorie ring, macro bars
```

### Example: User requests a 7-day meal plan

```
1. User clicks "Generate 7-Day Plan" on Meal Plan tab
2. Frontend POST /api/meal-plan  { "duration": 7 }
3. FastAPI router → MealPlanService.generate()
4. MealPlanService → loads user profile from DB
5. MealPlanService → AgentOrchestrator.dispatch("meal_plan", profile)
6. Orchestrator → DietRecommendationAgent.generate(profile)
7. DietRecAgent → computes calorie target (Harris-Benedict or Mifflin-St Jeor equation)
8. DietRecAgent → RAGRetriever.query("suitable foods for [dietary preference] [health condition]")
9. DietRecAgent → GraniteClient.generate(meal plan prompt with context + profile)
10. Granite returns structured JSON: 7 days × 3 meals + snacks
11. If profile has health conditions → HealthAdvisoryAgent.review(plan, conditions)
12. HealthAdvisoryAgent appends advisory note + disclaimer
13. Plan saved to DB, returned to frontend
14. Frontend renders meal cards with per-meal nutrition breakdown
```

---

## 12. API Endpoints

### Profile
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/profile` | Create or update user profile |
| GET | `/api/profile/{user_id}` | Retrieve user profile |

### Chat
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/chat` | Send a natural-language message; returns agent response |

### Food Log
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/log` | Log a food entry (food name, quantity, unit) |
| GET | `/api/log/today` | Get today's food log and nutritional totals |
| GET | `/api/log/history` | Get historical log entries (paginated) |
| DELETE | `/api/log/{entry_id}` | Delete a log entry |

### Meal Plan
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/meal-plan` | Generate a new meal plan (1-day or 7-day) |
| GET | `/api/meal-plan/latest` | Get the most recent meal plan |

### Dashboard
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/dashboard/daily` | Daily nutrient totals vs RDI targets |
| GET | `/api/dashboard/weekly` | Weekly calorie trend and goal progress |

### Health
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Service health check (liveness probe) |

### Request/Response Schema Example — POST `/api/log`

**Request:**
```json
{
  "user_id": "user_001",
  "food_name": "grilled chicken",
  "quantity": 200,
  "unit": "g",
  "meal_type": "lunch"
}
```

**Response:**
```json
{
  "entry_id": "log_20240115_001",
  "food_name": "Grilled Chicken Breast",
  "quantity_g": 200,
  "nutrition": {
    "calories": 330,
    "protein_g": 62,
    "carbs_g": 0,
    "fat_g": 7.2,
    "fiber_g": 0,
    "vitamins": { "B12_mcg": 1.6, "D_IU": 12 },
    "minerals": { "iron_mg": 1.8, "calcium_mg": 20 }
  },
  "daily_totals": { "calories": 1450, "protein_g": 98 },
  "feedback": "Great protein choice! You are at 87% of your daily protein goal.",
  "disclaimer": null
}
```

---

## 13. Project File / Folder Structure

```
NutriGenie/
├── README.md
├── PROJECT_BLUEPRINT.md
├── .env.example                  # Template showing required env vars (NO real values)
├── .gitignore                    # Excludes .env, __pycache__, data/chroma_db/, etc.
│
├── backend/
│   ├── main.py                   # FastAPI app entry point
│   ├── config.py                 # Settings (loads from env vars via pydantic-settings)
│   ├── requirements.txt
│   │
│   ├── routers/
│   │   ├── profile.py
│   │   ├── chat.py
│   │   ├── log.py
│   │   ├── meal_plan.py
│   │   └── dashboard.py
│   │
│   ├── services/
│   │   ├── profile_service.py
│   │   ├── log_service.py
│   │   ├── meal_plan_service.py
│   │   └── dashboard_service.py
│   │
│   ├── orchestration/
│   │   ├── orchestrator.py       # AgentOrchestrator — local router + watsonx Orch. adapter
│   │   └── intent_classifier.py  # Maps request type / classifies free-text intent
│   │
│   ├── agents/
│   │   ├── base_agent.py         # Base class with shared Granite + RAG wiring
│   │   ├── knowledge_agent.py    # Nutrition Knowledge Agent
│   │   ├── recommendation_agent.py  # Diet Recommendation Agent
│   │   ├── health_advisory_agent.py # Health Advisory Agent
│   │   └── food_log_agent.py     # Food Log & Feedback Agent
│   │
│   ├── ai/
│   │   ├── granite_client.py     # IBM Granite API wrapper
│   │   └── prompt_templates.py   # Prompt templates per agent
│   │
│   ├── rag/
│   │   ├── ingestor.py           # Loads raw data, chunks, embeds, stores in ChromaDB
│   │   ├── retriever.py          # Query ChromaDB, return top-k chunks
│   │   └── chroma_client.py      # ChromaDB client setup
│   │
│   ├── db/
│   │   ├── database.py           # SQLAlchemy engine + session
│   │   ├── models.py             # ORM models: User, FoodLogEntry, MealPlan
│   │   └── crud.py               # CRUD helper functions
│   │
│   └── schemas/
│       ├── profile.py
│       ├── log.py
│       ├── meal_plan.py
│       ├── chat.py
│       └── dashboard.py
│
├── data/
│   ├── raw/
│   │   ├── usda_foods_sample.json  # Curated USDA data (500 common foods)
│   │   ├── rdi_tables.md           # RDI reference tables
│   │   ├── condition_guidance/
│   │   │   ├── diabetes.md
│   │   │   ├── hypertension.md
│   │   │   └── anemia.md
│   │   └── cultural_foods/
│   │       ├── indian_foods.md
│   │       └── mediterranean_foods.md
│   └── chroma_db/                  # Auto-generated ChromaDB files (gitignored)
│
├── frontend/
│   ├── index.html                  # Main SPA shell
│   ├── style.css                   # Tailwind CSS or custom styles
│   ├── app.js                      # Tab routing, API calls, Chart.js setup
│   ├── components/
│   │   ├── profile.js
│   │   ├── chat.js
│   │   ├── food_log.js
│   │   ├── meal_plan.js
│   │   └── dashboard.js
│   └── assets/
│       └── logo.svg
│
├── scripts/
│   ├── ingest_knowledge_base.py    # One-time RAG ingestion script
│   └── seed_sample_data.py         # Seeds SQLite with demo profile + logs
│
├── tests/
│   ├── test_agents.py
│   ├── test_rag.py
│   ├── test_api.py
│   └── fixtures/
│       └── sample_profile.json
│
└── deployment/
    ├── Dockerfile
    ├── manifest.yml                # IBM Cloud Foundry manifest
    └── .dockerignore
```

---

## 14. Security and Privacy Considerations

### Credentials
- All IBM Cloud, watsonx.ai, and watsonx Orchestrate credentials are loaded exclusively from environment variables.
- `.env.example` documents the required variable names with placeholder values only.
- `.env` is in `.gitignore` and must never be committed.
- Required variables: `WATSONX_API_KEY`, `WATSONX_PROJECT_ID`, `WATSONX_URL`, `WATSONX_ORCHESTRATE_URL`, `WATSONX_ORCHESTRATE_INSTANCE_ID`, `SECRET_KEY` (FastAPI session), `DATABASE_URL`.

### User Data
- For MVP: user health data stored in local SQLite. No user data is sent to any third party except IBM Cloud (via the Granite API call, which includes only the relevant query context, never raw PII).
- Prompts sent to Granite are anonymized: user is referred to by profile attributes, not name or ID.
- Production: IBM Cloud Cloudant with encryption at rest and IBM IAM access control.

### API Security
- FastAPI endpoints protected with a simple session token for MVP.
- CORS configured to allow only the frontend origin.
- Production: IBM App ID or OAuth 2.0 for authentication.

### Medical Safety
- Health Advisory Agent prompt contains a hardcoded instruction: "Never diagnose, never prescribe, never claim to replace a medical professional."
- Disclaimer string is injected programmatically (not by the LLM) into every response from the Health Advisory Agent — ensuring it cannot be omitted by a model failure.

---

## 15. Error Handling and Fallback Behavior

| Scenario | Handling |
|----------|----------|
| Granite API timeout (>10s) | Retry once; if still failing, return a cached/stub response with a user-visible notice: "AI service is temporarily unavailable. Showing cached nutritional data." |
| Granite API auth failure | Log error server-side; return HTTP 503 with user message asking to try again later. |
| RAG returns no results | Agent uses general nutritional knowledge with disclaimer: "Specific data for this food was not found in the knowledge base. The following is general guidance." |
| Unknown food item in log | Prompt user to confirm the closest matching food from a suggested list (returned by RAG fuzzy match). |
| watsonx Orchestrate unavailable | Automatically fall back to local `AgentOrchestrator`. |
| DB write failure | Return error; do not partially commit log entries. |
| Invalid user input (missing required fields) | Pydantic validation returns HTTP 422 with a clear field-level error message. |
| Frontend JS error | Each component wrapped in try/catch; shows user-friendly toast message. |

---

## 16. Testing Strategy

### Unit Tests (`tests/`)
- `test_agents.py` — Each agent tested with mocked Granite responses and mocked RAG results. Verifies output schema and disclaimer presence.
- `test_rag.py` — Tests ingestion pipeline (chunking, embedding) and retrieval (top-k results for known queries).
- `test_api.py` — FastAPI TestClient integration tests for all endpoints; uses a test SQLite DB.

### Manual / Demo Tests
- End-to-end walkthrough using the seeded demo profile (`scripts/seed_sample_data.py`).
- Verify dashboard charts render correctly.
- Verify disclaimer appears on every Health Advisory response.
- Verify meal plan respects allergy constraints.

### Test Data
- `tests/fixtures/sample_profile.json` — A sample user profile covering a range of conditions for predictable test scenarios.

### What is NOT tested in MVP
- Load / performance testing.
- Security penetration testing.
- Full ChromaDB integration test (mocked for unit tests; tested manually via ingest script).

---

## 17. Local Development and Deployment

### Local Setup

```bash
# 1. Clone repository
git clone <repo_url>
cd NutriGenie

# 2. Backend setup
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt

# 3. Create .env from template
cp ../.env.example .env
# Edit .env and fill in real values (never commit this file)

# 4. Ingest knowledge base (one-time)
python ../scripts/ingest_knowledge_base.py

# 5. Seed demo data (optional)
python ../scripts/seed_sample_data.py

# 6. Run backend
uvicorn main:app --reload --port 8000

# 7. Frontend (in a separate terminal)
# Simply open frontend/index.html in a browser
# OR serve with a static file server:
cd ../frontend
python -m http.server 3000
```

### Environment Variable Reference (.env.example)

```
WATSONX_API_KEY=your_ibm_cloud_api_key_here
WATSONX_PROJECT_ID=your_watsonx_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_ORCHESTRATE_URL=https://api.dl.watson-orchestrate.ibm.com
WATSONX_ORCHESTRATE_INSTANCE_ID=your_orchestrate_instance_id_here
DATABASE_URL=sqlite:///./nutrigenie.db
SECRET_KEY=replace_with_a_random_secret_string
CHROMA_DB_PATH=../data/chroma_db
USE_LOCAL_ORCHESTRATOR=true
```

### IBM Cloud Deployment

```bash
# Build container
docker build -t nutrigenie-backend -f deployment/Dockerfile .

# Push to IBM Container Registry
ibmcloud cr login
docker tag nutrigenie-backend us.icr.io/<namespace>/nutrigenie-backend:latest
docker push us.icr.io/<namespace>/nutrigenie-backend:latest

# Deploy to IBM Cloud Code Engine
ibmcloud ce application create \
  --name nutrigenie \
  --image us.icr.io/<namespace>/nutrigenie-backend:latest \
  --env-from-secret nutrigenie-secrets
```

Frontend is deployed as a static site to IBM Cloud Object Storage + CDN or Cloud Foundry staticfile buildpack.

---

## 18. Future Scalability and Enhancements

| Enhancement | Description |
|-------------|-------------|
| **Production Vector DB** | Replace ChromaDB with IBM watsonx Discovery or Milvus on IBM Cloud for scalable RAG. |
| **Barcode / Photo Food Logging** | Integrate a food recognition API or camera barcode scan to log meals from product labels. |
| **Wearable Integration** | Sync with fitness trackers (Fitbit, Apple Health) to adjust calorie targets dynamically. |
| **Multilingual Support** | Add Indian regional language support (Hindi, Tamil, Telugu) using Granite multilingual models. |
| **Real-time Deficiency Alerts** | Push notifications when a user has consistently missed a micronutrient target. |
| **Community Recipes** | Crowdsourced recipe knowledge base with user ratings, fed back into the RAG store. |
| **Meal Photo Analysis** | Vision-capable model integration to estimate meal nutrition from a photo. |
| **Dietitian Referral Integration** | Connect users to registered dietitians when health conditions exceed safe self-service boundaries. |
| **IBM Cloudant** | Replace SQLite with Cloudant for multi-user production scalability. |
| **Fine-tuned Granite** | Fine-tune Granite on nutrition-specific corpora for improved domain accuracy. |

---

## 19. Step-by-Step Implementation Order

The following order minimizes dependency blockers and produces a demonstrable MVP as early as possible.

### Phase 1 — Foundation
- [ ] **Step 1**: Set up project folder structure as defined in Section 13. Create all empty files and directories.
- [ ] **Step 2**: Write `backend/config.py` — pydantic-settings class loading all env vars. Write `.env.example`.
- [ ] **Step 3**: Write `backend/db/` — SQLAlchemy models for User, FoodLogEntry, MealPlan. Initialize SQLite DB.
- [ ] **Step 4**: Write `backend/schemas/` — All Pydantic request/response schemas.
- [ ] **Step 5**: Write `backend/main.py` — FastAPI app, CORS, health check endpoint, router stubs.

### Phase 2 — RAG Pipeline
- [ ] **Step 6**: Curate `data/raw/` — Prepare USDA sample JSON (500 foods), RDI tables, condition guidance Markdown files.
- [ ] **Step 7**: Write `backend/rag/chroma_client.py` and `backend/rag/retriever.py`.
- [ ] **Step 8**: Write `backend/rag/ingestor.py` and `scripts/ingest_knowledge_base.py`. Run ingestion and verify.

### Phase 3 — AI / Agent Layer
- [ ] **Step 9**: Write `backend/ai/granite_client.py` — IBM Granite API wrapper with retry + timeout.
- [ ] **Step 10**: Write `backend/ai/prompt_templates.py` — Prompt templates for all four agents.
- [ ] **Step 11**: Write `backend/agents/base_agent.py` — Shared agent base class.
- [ ] **Step 12**: Write `backend/agents/knowledge_agent.py` — Nutrition Knowledge Agent.
- [ ] **Step 13**: Write `backend/agents/food_log_agent.py` — Food Log & Feedback Agent.
- [ ] **Step 14**: Write `backend/agents/recommendation_agent.py` — Diet Recommendation Agent.
- [ ] **Step 15**: Write `backend/agents/health_advisory_agent.py` — Health Advisory Agent with hardcoded disclaimer injection.
- [ ] **Step 16**: Write `backend/orchestration/intent_classifier.py` and `backend/orchestration/orchestrator.py`.

### Phase 4 — Backend API
- [ ] **Step 17**: Write `backend/services/profile_service.py` and `backend/routers/profile.py`. Test with curl/Postman.
- [ ] **Step 18**: Write `backend/services/log_service.py` and `backend/routers/log.py`. Test food logging end-to-end.
- [ ] **Step 19**: Write `backend/services/meal_plan_service.py` and `backend/routers/meal_plan.py`. Test meal plan generation.
- [ ] **Step 20**: Write `backend/routers/chat.py` — General chat endpoint routed through orchestrator.
- [ ] **Step 21**: Write `backend/services/dashboard_service.py` and `backend/routers/dashboard.py`.

### Phase 5 — Frontend
- [ ] **Step 22**: Write `frontend/index.html` — SPA shell with tab navigation (Profile, Chat, Log, Plan, Dashboard).
- [ ] **Step 23**: Write `frontend/components/profile.js` — Profile form with save.
- [ ] **Step 24**: Write `frontend/components/chat.js` — Chat panel with send/receive.
- [ ] **Step 25**: Write `frontend/components/food_log.js` — Log form + today's log table.
- [ ] **Step 26**: Write `frontend/components/meal_plan.js` — Plan generation + meal card display.
- [ ] **Step 27**: Write `frontend/components/dashboard.js` — Chart.js calorie ring, macro pie, weekly trend line.
- [ ] **Step 28**: Write `frontend/app.js` — Tab routing + global API utility.

### Phase 6 — Testing and Polish
- [ ] **Step 29**: Write `tests/test_agents.py`, `tests/test_rag.py`, `tests/test_api.py`. Run and fix.
- [ ] **Step 30**: Write `scripts/seed_sample_data.py`. Run end-to-end demo walkthrough.
- [ ] **Step 31**: Write `README.md` — Setup instructions, architecture summary, demo walkthrough.

### Phase 7 — Deployment
- [ ] **Step 32**: Write `deployment/Dockerfile`. Build and verify container runs locally.
- [ ] **Step 33**: Deploy to IBM Cloud Code Engine. Verify live endpoints.
- [ ] **Step 34**: Deploy frontend to IBM Cloud Object Storage or Cloud Foundry. Verify full stack works in production.

---

*Blueprint created for NutriGenie — AICTE / IBM Bob Hackathon submission.*
*Version 1.0 | Greenfield project | MVP-first, production-ready architecture.*
