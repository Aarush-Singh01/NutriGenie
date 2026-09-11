"""Profile service — CRUD operations for user profiles."""

from __future__ import annotations

from sqlalchemy.orm import Session

from db import crud
from db.models import UserProfile
from schemas.profile import ProfileCreate


def _list_to_str(value) -> str:
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return str(value) if value else ""


def upsert_profile(db: Session, data: ProfileCreate) -> UserProfile:
    db_data = {
        "age": data.age,
        "sex": data.sex,
        "height_cm": data.height_cm,
        "weight_kg": data.weight_kg,
        "activity_level": data.activity_level,
        "primary_goal": data.primary_goal,
        "dietary_preference": data.dietary_preference,
        "allergies": _list_to_str(data.allergies),
        "health_conditions": _list_to_str(data.health_conditions),
        "cuisine_preferences": data.cuisine_preferences,
    }
    return crud.upsert_user(db, data.user_id, db_data)


def get_profile(db: Session, user_id: str) -> UserProfile | None:
    return crud.get_user(db, user_id)


def profile_to_dict(user: UserProfile) -> dict:
    """Convert ORM model to a dict suitable for agent prompt context."""
    return {
        "user_id": user.id,
        "age": user.age,
        "sex": user.sex,
        "height_cm": user.height_cm,
        "weight_kg": user.weight_kg,
        "activity_level": user.activity_level,
        "primary_goal": user.primary_goal,
        "dietary_preference": user.dietary_preference,
        "allergies": user.allergies,
        "health_conditions": user.health_conditions,
        "cuisine_preferences": user.cuisine_preferences,
    }
