"""Pydantic schemas for meal plan requests and responses."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MealItem(BaseModel):
    name: str
    portion: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float


class DayPlan(BaseModel):
    day: int
    breakfast: List[MealItem] = []
    morning_snack: List[MealItem] = []
    lunch: List[MealItem] = []
    evening_snack: List[MealItem] = []
    dinner: List[MealItem] = []
    daily_calories: float = 0.0
    daily_protein_g: float = 0.0
    daily_carbs_g: float = 0.0
    daily_fat_g: float = 0.0


class MealPlanRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    duration_days: int = Field(default=1, ge=1, le=7)


class MealPlanResponse(BaseModel):
    plan_id: int
    user_id: str
    duration_days: int
    calorie_target: float
    days: List[DayPlan]
    health_advisory: Optional[str] = None
    disclaimer: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
