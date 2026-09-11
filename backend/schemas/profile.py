"""Pydantic schemas for user profile requests and responses."""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class ProfileCreate(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=64)
    age: int = Field(..., ge=1, le=120)
    sex: str = Field(..., pattern="^(male|female|other)$")
    height_cm: float = Field(..., gt=50, lt=300)
    weight_kg: float = Field(..., gt=10, lt=500)
    activity_level: str = Field(
        ...,
        pattern="^(sedentary|lightly_active|moderately_active|very_active|extra_active)$",
    )
    primary_goal: str = Field(
        ...,
        pattern="^(weight_loss|weight_gain|maintenance|muscle_gain|healthy_eating)$",
    )
    dietary_preference: str = Field(default="none")
    allergies: List[str] = Field(default_factory=list)
    health_conditions: List[str] = Field(default_factory=list)
    cuisine_preferences: str = Field(default="")


class ProfileResponse(BaseModel):
    user_id: str
    age: int
    sex: str
    height_cm: float
    weight_kg: float
    activity_level: str
    primary_goal: str
    dietary_preference: str
    allergies: List[str]
    health_conditions: List[str]
    cuisine_preferences: str

    model_config = {"from_attributes": True}
