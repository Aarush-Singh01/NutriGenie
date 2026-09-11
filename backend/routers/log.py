"""Food log router."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from db import crud
from schemas.log import LogRequest, LogEntryResponse, TodayLogResponse, NutritionInfo, DailyTotals
from services.log_service import create_log_entry, get_today_summary

router = APIRouter()


def _entry_to_response(entry) -> LogEntryResponse:
    return LogEntryResponse(
        entry_id=entry.id,
        food_name=entry.food_name,
        quantity_g=entry.quantity_g,
        meal_type=entry.meal_type,
        nutrition=NutritionInfo(
            calories=entry.calories,
            protein_g=entry.protein_g,
            carbs_g=entry.carbs_g,
            fat_g=entry.fat_g,
            fiber_g=entry.fiber_g,
        ),
        feedback=entry.feedback,
        logged_at=entry.logged_at,
    )


@router.post("/log", response_model=LogEntryResponse)
def log_food(request: LogRequest, db: Session = Depends(get_db)):
    try:
        result = create_log_entry(
            db,
            user_id=request.user_id,
            food_name=request.food_name,
            quantity=request.quantity,
            unit=request.unit,
            meal_type=request.meal_type,
        )
        return _entry_to_response(result["entry"])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/log/today", response_model=TodayLogResponse)
def today_log(user_id: str, db: Session = Depends(get_db)):
    summary = get_today_summary(db, user_id)
    return TodayLogResponse(
        entries=[_entry_to_response(e) for e in summary["entries"]],
        daily_totals=DailyTotals(**summary["daily_totals"]),
        calorie_target=summary["calorie_target"],
        protein_target_g=summary["protein_target_g"],
    )


@router.get("/log/history", response_model=List[LogEntryResponse])
def log_history(user_id: str, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    entries = crud.get_log_history(db, user_id, skip=skip, limit=limit)
    return [_entry_to_response(e) for e in entries]


@router.delete("/log/{entry_id}")
def delete_log(entry_id: int, user_id: str, db: Session = Depends(get_db)):
    deleted = crud.delete_log_entry(db, entry_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Log entry not found")
    return {"deleted": True, "entry_id": entry_id}
