"""NutriGenie FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from db.database import init_db
from routers import profile, chat, log, meal_plan, dashboard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nutrigenie")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialise DB tables on startup."""
    logger.info("NutriGenie starting up — initialising database …")
    init_db()
    logger.info("Database ready.")
    yield
    logger.info("NutriGenie shutting down.")


app = FastAPI(
    title="NutriGenie API",
    description="AI-Powered Personalized Nutrition Agent",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ─────────────────────────────────────────────────────────────────
app.include_router(profile.router, prefix="/api", tags=["profile"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(log.router, prefix="/api", tags=["log"])
app.include_router(meal_plan.router, prefix="/api", tags=["meal-plan"])
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])


@app.get("/api/health", tags=["health"])
async def health_check() -> dict:
    """Liveness probe — returns 200 if the service is running."""
    return {
        "status": "ok",
        "service": "NutriGenie API",
        "version": "1.0.0",
        "local_orchestrator": settings.use_local_orchestrator,
    }
