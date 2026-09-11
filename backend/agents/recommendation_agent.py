"""
Diet Recommendation Agent.

Computes calorie/macro targets using Mifflin-St Jeor equation,
retrieves suitable foods via RAG, calls Granite to generate a structured meal plan.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Optional

from agents.base_agent import BaseAgent
from ai.prompt_templates import recommendation_prompt

logger = logging.getLogger(__name__)


def compute_calorie_target(profile: dict) -> float:
    """
    Compute daily calorie target using the Mifflin-St Jeor equation.

    BMR:
      Male:   10×weight_kg + 6.25×height_cm − 5×age + 5
      Female: 10×weight_kg + 6.25×height_cm − 5×age − 161

    Activity multipliers:
      sedentary           → 1.2
      lightly_active      → 1.375
      moderately_active   → 1.55
      very_active         → 1.725
      extra_active        → 1.9
    """
    weight = float(profile.get("weight_kg", 70))
    height = float(profile.get("height_cm", 170))
    age = int(profile.get("age", 30))
    sex = str(profile.get("sex", "male")).lower()

    if sex == "female":
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age + 5

    activity_multipliers = {
        "sedentary": 1.2,
        "lightly_active": 1.375,
        "moderately_active": 1.55,
        "very_active": 1.725,
        "extra_active": 1.9,
    }
    multiplier = activity_multipliers.get(
        str(profile.get("activity_level", "moderately_active")), 1.55
    )
    tdee = bmr * multiplier

    goal = str(profile.get("primary_goal", "maintenance")).lower()
    if goal == "weight_loss":
        return tdee - 500
    if goal == "weight_gain" or goal == "muscle_gain":
        return tdee + 300
    return tdee  # maintenance / healthy_eating


class RecommendationAgent(BaseAgent):
    agent_name = "diet_recommendation"

    def generate_plan(self, profile: dict, days: int = 1, extra_query: str = "") -> dict:
        """
        Generate a personalized meal plan.

        Returns:
            {
                "calorie_target": float,
                "days": [ { day_plan dict } ],
                "raw_response": str,
                "agent": str,
            }
        """
        calorie_target = compute_calorie_target(profile)

        dietary_pref = profile.get("dietary_preference", "none")
        health_conds = profile.get("health_conditions", "none")
        allergies = profile.get("allergies", "none")
        rag_query = (
            f"suitable foods for {dietary_pref} diet "
            f"health conditions {health_conds} "
            f"avoid {allergies} Indian meal plan"
        )
        context = self._retrieve_context(rag_query, top_k=5)

        prompt = recommendation_prompt(
            query=extra_query or f"Generate a {days}-day Indian meal plan.",
            rag_context=context,
            profile=profile,
            calorie_target=calorie_target,
            days=days,
        )
        raw = self._generate(prompt, max_new_tokens=1000)

        days_data = self._parse_plan(raw, days, calorie_target)
        return {
            "calorie_target": calorie_target,
            "days": days_data,
            "raw_response": raw,
            "agent": self.agent_name,
        }

    def _parse_plan(self, raw: str, days: int, calorie_target: float) -> list:
        """
        Parse LLM output. Tries JSON block first; falls back to a structured default plan.
        """
        match = re.search(r"```json\s*(.*?)\s*```", raw, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                if isinstance(data, list):
                    return data
                if isinstance(data, dict) and "days" in data:
                    return data["days"]
            except (json.JSONDecodeError, ValueError):
                pass

        # Build a default fallback plan
        return self._default_plan(days, calorie_target)

    def _default_plan(self, days: int, calorie_target: float) -> list:
        """Return a generic Indian meal plan template when JSON parsing fails."""
        per_meal_cal = calorie_target / 5  # 5 eating occasions
        result = []
        for d in range(1, days + 1):
            result.append(
                {
                    "day": d,
                    "breakfast": [
                        {
                            "name": "Oats porridge with milk and banana",
                            "portion": "1 bowl + 1 banana",
                            "calories": round(per_meal_cal * 0.22),
                            "protein_g": 10,
                            "carbs_g": 45,
                            "fat_g": 5,
                        }
                    ],
                    "morning_snack": [
                        {
                            "name": "A handful of mixed nuts + 1 apple",
                            "portion": "30g nuts + 1 apple",
                            "calories": round(per_meal_cal * 0.12),
                            "protein_g": 5,
                            "carbs_g": 20,
                            "fat_g": 8,
                        }
                    ],
                    "lunch": [
                        {
                            "name": "2 whole wheat roti + toor dal + mixed vegetable sabzi + curd",
                            "portion": "2 roti + 1 katori dal + 1 katori sabzi + 100g curd",
                            "calories": round(per_meal_cal * 0.30),
                            "protein_g": 18,
                            "carbs_g": 55,
                            "fat_g": 8,
                        }
                    ],
                    "evening_snack": [
                        {
                            "name": "Moong dal chilla / sprouts chaat",
                            "portion": "2 pieces / 1 small bowl",
                            "calories": round(per_meal_cal * 0.12),
                            "protein_g": 8,
                            "carbs_g": 20,
                            "fat_g": 3,
                        }
                    ],
                    "dinner": [
                        {
                            "name": "Brown rice + rajma / chickpea curry + palak sabzi",
                            "portion": "1 katori rice + 1 katori rajma + 1 katori palak",
                            "calories": round(per_meal_cal * 0.24),
                            "protein_g": 16,
                            "carbs_g": 50,
                            "fat_g": 6,
                        }
                    ],
                    "daily_calories": round(calorie_target),
                    "daily_protein_g": 57,
                    "daily_carbs_g": 190,
                    "daily_fat_g": 30,
                }
            )
        return result
