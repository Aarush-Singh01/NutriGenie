"""Meal plan service — generates and persists meal plans."""

from __future__ import annotations

import json
import logging
from typing import Optional

from sqlalchemy.orm import Session

from db import crud
from orchestration.orchestrator import orchestrator
from services.profile_service import get_profile, profile_to_dict

logger = logging.getLogger(__name__)


def generate_meal_plan(db: Session, user_id: str, duration_days: int = 1) -> dict:
    """Generate a meal plan and persist it to the database."""
    profile = get_profile(db, user_id)
    if not profile:
        raise ValueError(f"No profile found for user_id={user_id}. Please create a profile first.")

    profile_dict = profile_to_dict(profile)

    result = orchestrator.dispatch(
        message=f"Generate a {duration_days}-day personalized meal plan.",
        profile=profile_dict,
        request_type="meal_plan",
        plan_days=duration_days,
    )

    calorie_target = result.get("calorie_target", 2000.0)
    days_data = result.get("days", [])

    plan_data = {
        "duration_days": duration_days,
        "plan_json": json.dumps({"days": days_data, "raw_response": result.get("raw_response", "")}),
        "calorie_target": calorie_target,
    }
    plan = crud.create_meal_plan(db, user_id, plan_data)

    return {
        "plan": plan,
        "days": days_data,
        "calorie_target": calorie_target,
        "health_advisory": None,
        "disclaimer": result.get("disclaimer"),
    }


def get_latest_plan(db: Session, user_id: str) -> Optional[dict]:
    plan = crud.get_latest_meal_plan(db, user_id)
    if not plan:
        return None
    data = json.loads(plan.plan_json)
    return {
        "plan": plan,
        "days": data.get("days", []),
        "calorie_target": plan.calorie_target,
        "health_advisory": None,
        "disclaimer": None,
    }
