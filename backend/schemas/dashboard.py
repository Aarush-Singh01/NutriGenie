"""Pydantic schemas for dashboard endpoints."""

from __future__ import annotations

from typing import List
from pydantic import BaseModel


class NutrientProgress(BaseModel):
    name: str
    current: float
    target: float
    unit: str
    percent: float


class DailyDashboard(BaseModel):
    user_id: str
    calorie_consumed: float
    calorie_target: float
    calorie_percent: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    protein_target_g: float
    carbs_target_g: float
    fat_target_g: float
    nutrients: List[NutrientProgress]


class WeeklyDataPoint(BaseModel):
    date: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float


class WeeklyDashboard(BaseModel):
    user_id: str
    calorie_target: float
    weekly_data: List[WeeklyDataPoint]
    avg_calories: float
    goal_hit_days: int
