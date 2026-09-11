"""Meal plan router."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from schemas.meal_plan import MealPlanRequest, MealPlanResponse, DayPlan, MealItem
from services.meal_plan_service import generate_meal_plan, get_latest_plan

router = APIRouter()


def _days_to_schema(days_data: list) -> list[DayPlan]:
    result = []
    for d in days_data:
        def _meals(key: str) -> list[MealItem]:
            items = d.get(key, [])
            out = []
            for item in items:
                if isinstance(item, dict):
                    out.append(
                        MealItem(
                            name=item.get("name", ""),
                            portion=item.get("portion", ""),
                            calories=float(item.get("calories", 0)),
                            protein_g=float(item.get("protein_g", 0)),
                            carbs_g=float(item.get("carbs_g", 0)),
                            fat_g=float(item.get("fat_g", 0)),
                        )
                    )
            return out

        result.append(
            DayPlan(
                day=d.get("day", 1),
                breakfast=_meals("breakfast"),
                morning_snack=_meals("morning_snack"),
                lunch=_meals("lunch"),
                evening_snack=_meals("evening_snack"),
                dinner=_meals("dinner"),
                daily_calories=float(d.get("daily_calories", 0)),
                daily_protein_g=float(d.get("daily_protein_g", 0)),
                daily_carbs_g=float(d.get("daily_carbs_g", 0)),
                daily_fat_g=float(d.get("daily_fat_g", 0)),
            )
        )
    return result


@router.post("/meal-plan", response_model=MealPlanResponse)
def create_meal_plan(request: MealPlanRequest, db: Session = Depends(get_db)):
    try:
        result = generate_meal_plan(db, request.user_id, request.duration_days)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    plan = result["plan"]
    return MealPlanResponse(
        plan_id=plan.id,
        user_id=request.user_id,
        duration_days=plan.duration_days,
        calorie_target=plan.calorie_target,
        days=_days_to_schema(result["days"]),
        health_advisory=result.get("health_advisory"),
        disclaimer=result.get("disclaimer"),
        created_at=plan.created_at,
    )


@router.get("/meal-plan/latest", response_model=Optional[MealPlanResponse])
def latest_meal_plan(user_id: str, db: Session = Depends(get_db)):
    result = get_latest_plan(db, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="No meal plan found for this user")
    plan = result["plan"]
    return MealPlanResponse(
        plan_id=plan.id,
        user_id=user_id,
        duration_days=plan.duration_days,
        calorie_target=plan.calorie_target,
        days=_days_to_schema(result["days"]),
        health_advisory=result.get("health_advisory"),
        disclaimer=result.get("disclaimer"),
        created_at=plan.created_at,
    )
