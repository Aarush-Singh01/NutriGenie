"""Pydantic schemas for chat requests and responses."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1, max_length=2000)
    request_type: Optional[str] = Field(
        default=None,
        description=(
            "Optional hint: 'nutrition_query' | 'meal_plan' | "
            "'food_log' | 'health_advice' | 'dashboard'. "
            "If omitted the orchestrator will classify automatically."
        ),
    )


class ChatResponse(BaseModel):
    response: str
    agent_used: str
    disclaimer: Optional[str] = None
