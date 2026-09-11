"""Food log service — creates log entries and computes daily totals."""

from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy.orm import Session

from db import crud
from db.models import UserProfile, FoodLogEntry
from orchestration.orchestrator import orchestrator
from services.profile_service import get_profile, profile_to_dict

logger = logging.getLogger(__name__)

# Approximate daily targets (defaults when no profile is available)
DEFAULT_CALORIE_TARGET = 2000.0
DEFAULT_PROTEIN_TARGET = 60.0


def _unit_to_grams(quantity: float, unit: str) -> float:
    """Convert common units to grams."""
    unit_lower = unit.lower().strip()
    conversions = {
        "g": 1.0,
        "grams": 1.0,
        "gram": 1.0,
        "kg": 1000.0,
        "oz": 28.35,
        "lb": 453.59,
        "ml": 1.0,     # approximate for liquids
        "l": 1000.0,
        "cup": 240.0,
        "tbsp": 15.0,
        "tsp": 5.0,
        "piece": 100.0,
        "pieces": 100.0,
        "serving": 100.0,
    }
    return quantity * conversions.get(unit_lower, 1.0)


def _compute_totals(entries: list[FoodLogEntry]) -> dict:
    totals = {"calories": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0, "fiber_g": 0.0}
    for e in entries:
        totals["calories"] += e.calories
        totals["protein_g"] += e.protein_g
        totals["carbs_g"] += e.carbs_g
        totals["fat_g"] += e.fat_g
        totals["fiber_g"] += e.fiber_g
    totals["entries_count"] = len(entries)
    return totals


def create_log_entry(
    db: Session, user_id: str, food_name: str, quantity: float, unit: str, meal_type: str
) -> dict:
    quantity_g = _unit_to_grams(quantity, unit)

    profile = get_profile(db, user_id)
    profile_dict = profile_to_dict(profile) if profile else None

    today_entries = crud.get_today_logs(db, user_id)
    daily_totals = _compute_totals(today_entries)

    result = orchestrator.dispatch(
        message=f"Log food: {quantity_g}g of {food_name}",
        profile=profile_dict,
        request_type="food_log",
        food_name=food_name,
        quantity_g=quantity_g,
        daily_totals=daily_totals,
    )

    nutrition = result.get("nutrition", {})
    entry_data = {
        "food_name": food_name,
        "quantity_g": quantity_g,
        "meal_type": meal_type,
        "calories": nutrition.get("calories", 0.0),
        "protein_g": nutrition.get("protein_g", 0.0),
        "carbs_g": nutrition.get("carbs_g", 0.0),
        "fat_g": nutrition.get("fat_g", 0.0),
        "fiber_g": nutrition.get("fiber_g", 0.0),
        "feedback": result.get("response", ""),
    }
    entry = crud.create_log_entry(db, user_id, entry_data)
    return {"entry": entry, "result": result}


def get_today_summary(db: Session, user_id: str) -> dict:
    entries = crud.get_today_logs(db, user_id)
    totals = _compute_totals(entries)

    profile = get_profile(db, user_id)
    calorie_target = DEFAULT_CALORIE_TARGET
    protein_target = DEFAULT_PROTEIN_TARGET

    if profile:
        from agents.recommendation_agent import compute_calorie_target
        calorie_target = compute_calorie_target(profile_to_dict(profile))
        protein_target = float(profile.weight_kg) * 0.8

    return {
        "entries": entries,
        "daily_totals": totals,
        "calorie_target": calorie_target,
        "protein_target_g": protein_target,
    }
