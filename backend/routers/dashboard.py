"""Dashboard router."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.database import get_db
from schemas.dashboard import DailyDashboard, WeeklyDashboard, NutrientProgress, WeeklyDataPoint
from services.dashboard_service import get_daily_dashboard, get_weekly_dashboard

router = APIRouter()


@router.get("/dashboard/daily", response_model=DailyDashboard)
def daily_dashboard(user_id: str, db: Session = Depends(get_db)):
    data = get_daily_dashboard(db, user_id)
    return DailyDashboard(
        user_id=data["user_id"],
        calorie_consumed=data["calorie_consumed"],
        calorie_target=data["calorie_target"],
        calorie_percent=data["calorie_percent"],
        protein_g=data["protein_g"],
        carbs_g=data["carbs_g"],
        fat_g=data["fat_g"],
        fiber_g=data["fiber_g"],
        protein_target_g=data["protein_target_g"],
        carbs_target_g=data["carbs_target_g"],
        fat_target_g=data["fat_target_g"],
        nutrients=[NutrientProgress(**n) for n in data["nutrients"]],
    )


@router.get("/dashboard/weekly", response_model=WeeklyDashboard)
def weekly_dashboard(user_id: str, db: Session = Depends(get_db)):
    data = get_weekly_dashboard(db, user_id)
    return WeeklyDashboard(
        user_id=data["user_id"],
        calorie_target=data["calorie_target"],
        weekly_data=[WeeklyDataPoint(**w) for w in data["weekly_data"]],
        avg_calories=data["avg_calories"],
        goal_hit_days=data["goal_hit_days"],
    )
