"""Pydantic schemas for food log requests and responses."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class NutritionInfo(BaseModel):
    calories: float = 0.0
    protein_g: float = 0.0
    carbs_g: float = 0.0
    fat_g: float = 0.0
    fiber_g: float = 0.0


class DailyTotals(BaseModel):
    calories: float = 0.0
    protein_g: float = 0.0
    carbs_g: float = 0.0
    fat_g: float = 0.0
    fiber_g: float = 0.0
    entries_count: int = 0


class LogRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    food_name: str = Field(..., min_length=1, max_length=256)
    quantity: float = Field(..., gt=0)
    unit: str = Field(default="g")
    meal_type: str = Field(default="other")


class LogEntryResponse(BaseModel):
    entry_id: int
    food_name: str
    quantity_g: float
    meal_type: str
    nutrition: NutritionInfo
    feedback: str
    logged_at: datetime

    model_config = {"from_attributes": True}


class TodayLogResponse(BaseModel):
    entries: list[LogEntryResponse]
    daily_totals: DailyTotals
    calorie_target: float
    protein_target_g: float
