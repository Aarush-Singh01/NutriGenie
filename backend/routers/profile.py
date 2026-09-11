"""Profile router."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from schemas.profile import ProfileCreate, ProfileResponse
from services.profile_service import upsert_profile, get_profile

router = APIRouter()


@router.post("/profile", response_model=ProfileResponse)
def create_or_update_profile(data: ProfileCreate, db: Session = Depends(get_db)):
    user = upsert_profile(db, data)
    return ProfileResponse(
        user_id=user.id,
        age=user.age,
        sex=user.sex,
        height_cm=user.height_cm,
        weight_kg=user.weight_kg,
        activity_level=user.activity_level,
        primary_goal=user.primary_goal,
        dietary_preference=user.dietary_preference,
        allergies=[a.strip() for a in user.allergies.split(",") if a.strip()],
        health_conditions=[h.strip() for h in user.health_conditions.split(",") if h.strip()],
        cuisine_preferences=user.cuisine_preferences,
    )


@router.get("/profile/{user_id}", response_model=ProfileResponse)
def read_profile(user_id: str, db: Session = Depends(get_db)):
    user = get_profile(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Profile not found")
    return ProfileResponse(
        user_id=user.id,
        age=user.age,
        sex=user.sex,
        height_cm=user.height_cm,
        weight_kg=user.weight_kg,
        activity_level=user.activity_level,
        primary_goal=user.primary_goal,
        dietary_preference=user.dietary_preference,
        allergies=[a.strip() for a in user.allergies.split(",") if a.strip()],
        health_conditions=[h.strip() for h in user.health_conditions.split(",") if h.strip()],
        cuisine_preferences=user.cuisine_preferences,
    )
