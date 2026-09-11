"""Dashboard service — aggregates daily and weekly nutrition data."""

from __future__ import annotations

import datetime
from collections import defaultdict

from sqlalchemy.orm import Session

from db import crud
from services.profile_service import get_profile, profile_to_dict

# Default RDI targets (used when no profile available)
DEFAULT_TARGETS = {
    "calories": 2000.0,
    "protein_g": 60.0,
    "carbs_g": 250.0,
    "fat_g": 65.0,
    "fiber_g": 30.0,
}


def _compute_targets(profile_dict: dict) -> dict:
    from agents.recommendation_agent import compute_calorie_target
    calories = compute_calorie_target(profile_dict)
    return {
        "calories": calories,
        "protein_g": calories * 0.25 / 4,    # 25% calories from protein
        "carbs_g": calories * 0.50 / 4,      # 50% from carbs
        "fat_g": calories * 0.25 / 9,        # 25% from fat
        "fiber_g": 30.0,
    }


def get_daily_dashboard(db: Session, user_id: str) -> dict:
    entries = crud.get_today_logs(db, user_id)

    totals = {"calories": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0, "fiber_g": 0.0}
    for e in entries:
        totals["calories"] += e.calories
        totals["protein_g"] += e.protein_g
        totals["carbs_g"] += e.carbs_g
        totals["fat_g"] += e.fat_g
        totals["fiber_g"] += e.fiber_g

    profile = get_profile(db, user_id)
    targets = _compute_targets(profile_to_dict(profile)) if profile else DEFAULT_TARGETS

    def pct(current: float, target: float) -> float:
        return round((current / target * 100) if target > 0 else 0, 1)

    nutrients = [
        {
            "name": "Calories",
            "current": round(totals["calories"], 1),
            "target": round(targets["calories"], 1),
            "unit": "kcal",
            "percent": pct(totals["calories"], targets["calories"]),
        },
        {
            "name": "Protein",
            "current": round(totals["protein_g"], 1),
            "target": round(targets["protein_g"], 1),
            "unit": "g",
            "percent": pct(totals["protein_g"], targets["protein_g"]),
        },
        {
            "name": "Carbohydrates",
            "current": round(totals["carbs_g"], 1),
            "target": round(targets["carbs_g"], 1),
            "unit": "g",
            "percent": pct(totals["carbs_g"], targets["carbs_g"]),
        },
        {
            "name": "Fat",
            "current": round(totals["fat_g"], 1),
            "target": round(targets["fat_g"], 1),
            "unit": "g",
            "percent": pct(totals["fat_g"], targets["fat_g"]),
        },
        {
            "name": "Fiber",
            "current": round(totals["fiber_g"], 1),
            "target": round(targets["fiber_g"], 1),
            "unit": "g",
            "percent": pct(totals["fiber_g"], targets["fiber_g"]),
        },
    ]

    return {
        "user_id": user_id,
        "calorie_consumed": round(totals["calories"], 1),
        "calorie_target": round(targets["calories"], 1),
        "calorie_percent": pct(totals["calories"], targets["calories"]),
        "protein_g": round(totals["protein_g"], 1),
        "carbs_g": round(totals["carbs_g"], 1),
        "fat_g": round(totals["fat_g"], 1),
        "fiber_g": round(totals["fiber_g"], 1),
        "protein_target_g": round(targets["protein_g"], 1),
        "carbs_target_g": round(targets["carbs_g"], 1),
        "fat_target_g": round(targets["fat_g"], 1),
        "nutrients": nutrients,
    }


def get_weekly_dashboard(db: Session, user_id: str) -> dict:
    entries = crud.get_weekly_logs(db, user_id, days=7)

    profile = get_profile(db, user_id)
    targets = _compute_targets(profile_to_dict(profile)) if profile else DEFAULT_TARGETS
    calorie_target = targets["calories"]

    # Aggregate by date
    by_date: dict = defaultdict(lambda: {"calories": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0})
    for e in entries:
        date_key = e.logged_at.strftime("%Y-%m-%d")
        by_date[date_key]["calories"] += e.calories
        by_date[date_key]["protein_g"] += e.protein_g
        by_date[date_key]["carbs_g"] += e.carbs_g
        by_date[date_key]["fat_g"] += e.fat_g

    # Ensure all 7 days are present (even with 0 data)
    weekly_data = []
    goal_hit_days = 0
    total_cal = 0.0
    for i in range(6, -1, -1):
        day = (datetime.date.today() - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        row = by_date.get(day, {"calories": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0})
        cal = round(row["calories"], 1)
        total_cal += cal
        if calorie_target * 0.85 <= cal <= calorie_target * 1.15:
            goal_hit_days += 1
        weekly_data.append(
            {
                "date": day,
                "calories": cal,
                "protein_g": round(row["protein_g"], 1),
                "carbs_g": round(row["carbs_g"], 1),
                "fat_g": round(row["fat_g"], 1),
            }
        )

    days_with_data = sum(1 for w in weekly_data if w["calories"] > 0)
    avg_cal = round(total_cal / max(days_with_data, 1), 1)

    return {
        "user_id": user_id,
        "calorie_target": round(calorie_target, 1),
        "weekly_data": weekly_data,
        "avg_calories": avg_cal,
        "goal_hit_days": goal_hit_days,
    }
