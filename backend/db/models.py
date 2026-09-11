"""SQLAlchemy ORM models for NutriGenie."""

from __future__ import annotations

import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    sex: Mapped[str] = mapped_column(String(16), nullable=False)
    height_cm: Mapped[float] = mapped_column(Float, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    activity_level: Mapped[str] = mapped_column(String(32), nullable=False)
    primary_goal: Mapped[str] = mapped_column(String(64), nullable=False)
    dietary_preference: Mapped[str] = mapped_column(String(64), default="")
    allergies: Mapped[str] = mapped_column(Text, default="")          # comma-separated
    health_conditions: Mapped[str] = mapped_column(Text, default="")  # comma-separated
    cuisine_preferences: Mapped[str] = mapped_column(Text, default="")

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    food_logs: Mapped[list[FoodLogEntry]] = relationship(
        "FoodLogEntry", back_populates="user", cascade="all, delete-orphan"
    )
    meal_plans: Mapped[list[MealPlan]] = relationship(
        "MealPlan", back_populates="user", cascade="all, delete-orphan"
    )


class FoodLogEntry(Base):
    __tablename__ = "food_log_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("user_profiles.id"), nullable=False
    )
    food_name: Mapped[str] = mapped_column(String(256), nullable=False)
    quantity_g: Mapped[float] = mapped_column(Float, nullable=False)
    meal_type: Mapped[str] = mapped_column(String(32), default="other")

    # Nutritional values (per logged quantity)
    calories: Mapped[float] = mapped_column(Float, default=0.0)
    protein_g: Mapped[float] = mapped_column(Float, default=0.0)
    carbs_g: Mapped[float] = mapped_column(Float, default=0.0)
    fat_g: Mapped[float] = mapped_column(Float, default=0.0)
    fiber_g: Mapped[float] = mapped_column(Float, default=0.0)

    feedback: Mapped[str] = mapped_column(Text, default="")
    logged_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    user: Mapped[UserProfile] = relationship("UserProfile", back_populates="food_logs")


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("user_profiles.id"), nullable=False
    )
    duration_days: Mapped[int] = mapped_column(Integer, default=1)
    plan_json: Mapped[str] = mapped_column(Text, nullable=False)  # JSON blob
    calorie_target: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    user: Mapped[UserProfile] = relationship("UserProfile", back_populates="meal_plans")
