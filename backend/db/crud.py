"""CRUD helper functions — all DB access goes through here (no raw SQL)."""

from __future__ import annotations

import datetime
from typing import Optional, List

from sqlalchemy.orm import Session

from db.models import UserProfile, FoodLogEntry, MealPlan


# ── User Profile ────────────────────────────────────────────────────────────

def get_user(db: Session, user_id: str) -> Optional[UserProfile]:
    return db.query(UserProfile).filter(UserProfile.id == user_id).first()


def upsert_user(db: Session, user_id: str, data: dict) -> UserProfile:
    user = get_user(db, user_id)
    if user is None:
        user = UserProfile(id=user_id, **data)
        db.add(user)
    else:
        for key, value in data.items():
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


# ── Food Log ────────────────────────────────────────────────────────────────

def create_log_entry(db: Session, user_id: str, data: dict) -> FoodLogEntry:
    entry = FoodLogEntry(user_id=user_id, **data)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_today_logs(db: Session, user_id: str) -> List[FoodLogEntry]:
    today = datetime.date.today()
    start = datetime.datetime(today.year, today.month, today.day)
    end = start + datetime.timedelta(days=1)
    return (
        db.query(FoodLogEntry)
        .filter(
            FoodLogEntry.user_id == user_id,
            FoodLogEntry.logged_at >= start,
            FoodLogEntry.logged_at < end,
        )
        .order_by(FoodLogEntry.logged_at)
        .all()
    )


def get_log_history(
    db: Session, user_id: str, skip: int = 0, limit: int = 50
) -> List[FoodLogEntry]:
    return (
        db.query(FoodLogEntry)
        .filter(FoodLogEntry.user_id == user_id)
        .order_by(FoodLogEntry.logged_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def delete_log_entry(db: Session, entry_id: int, user_id: str) -> bool:
    entry = (
        db.query(FoodLogEntry)
        .filter(FoodLogEntry.id == entry_id, FoodLogEntry.user_id == user_id)
        .first()
    )
    if entry is None:
        return False
    db.delete(entry)
    db.commit()
    return True


def get_weekly_logs(db: Session, user_id: str, days: int = 7) -> List[FoodLogEntry]:
    cutoff = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) - datetime.timedelta(days=days)
    return (
        db.query(FoodLogEntry)
        .filter(FoodLogEntry.user_id == user_id, FoodLogEntry.logged_at >= cutoff)
        .order_by(FoodLogEntry.logged_at)
        .all()
    )


# ── Meal Plan ───────────────────────────────────────────────────────────────

def create_meal_plan(db: Session, user_id: str, data: dict) -> MealPlan:
    plan = MealPlan(user_id=user_id, **data)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def get_latest_meal_plan(db: Session, user_id: str) -> Optional[MealPlan]:
    return (
        db.query(MealPlan)
        .filter(MealPlan.user_id == user_id)
        .order_by(MealPlan.created_at.desc())
        .first()
    )
