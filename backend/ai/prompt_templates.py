"""
Prompt templates for all four NutriGenie agents.

All templates use the structured format:
  [SYSTEM] / [CONTEXT] / [USER PROFILE] / [USER REQUEST] / [RESPONSE]
Max input budget: 3,000 tokens; max output: 1,000 tokens.
"""

from __future__ import annotations
from typing import Optional


def _profile_section(profile: Optional[dict]) -> str:
    if not profile:
        return "[USER PROFILE]\nNo profile available.\n"
    return (
        "[USER PROFILE]\n"
        f"Age: {profile.get('age', 'N/A')}, "
        f"Sex: {profile.get('sex', 'N/A')}, "
        f"Height: {profile.get('height_cm', 'N/A')}cm, "
        f"Weight: {profile.get('weight_kg', 'N/A')}kg\n"
        f"Activity level: {profile.get('activity_level', 'N/A')}\n"
        f"Goal: {profile.get('primary_goal', 'N/A')}\n"
        f"Dietary preference: {profile.get('dietary_preference', 'none')}\n"
        f"Allergies: {profile.get('allergies', 'none')}\n"
        f"Health conditions: {profile.get('health_conditions', 'none')}\n"
        f"Cuisine preferences: {profile.get('cuisine_preferences', 'Indian')}\n"
    )


# ── Agent 1 — Nutrition Knowledge ────────────────────────────────────────────

KNOWLEDGE_SYSTEM = (
    "[SYSTEM]\n"
    "You are a factual nutrition information assistant. "
    "Your role is to provide accurate nutritional data about foods and nutrients. "
    "Always ground your answer in the provided context. "
    "Report approximate values clearly as approximate. "
    "Do not make specific medical claims or diagnose conditions. "
    "Only report nutritional data.\n"
)


def knowledge_prompt(query: str, rag_context: str, profile: Optional[dict] = None) -> str:
    return (
        f"{KNOWLEDGE_SYSTEM}\n"
        f"[CONTEXT]\n{rag_context}\n\n"
        f"{_profile_section(profile)}\n"
        f"[USER REQUEST]\n{query}\n\n"
        "[RESPONSE]\n"
    )


# ── Agent 2 — Diet Recommendation ────────────────────────────────────────────

RECOMMENDATION_SYSTEM = (
    "[SYSTEM]\n"
    "You are a personalized diet recommendation assistant. "
    "Generate a practical, culturally appropriate meal plan based on the user profile and goals. "
    "Use the knowledge base context to select suitable foods. "
    "Include breakfast, morning snack, lunch, evening snack, and dinner. "
    "Provide approximate calories, protein (g), carbohydrates (g), and fat (g) per meal. "
    "Respect all dietary preferences, allergies, and health conditions strictly. "
    "Prioritize Indian foods where appropriate. "
    "Respond with a clear structured meal plan in JSON format inside ```json ... ``` code block "
    "followed by a brief note. "
    "Never diagnose conditions or recommend medications.\n"
)


def recommendation_prompt(
    query: str, rag_context: str, profile: dict, calorie_target: float, days: int = 1
) -> str:
    return (
        f"{RECOMMENDATION_SYSTEM}\n"
        f"[CONTEXT]\n{rag_context}\n\n"
        f"{_profile_section(profile)}\n"
        f"[CALORIE TARGET]\nApproximate daily calorie target: {calorie_target:.0f} kcal\n"
        f"[MACRO TARGETS]\n"
        f"Protein: {calorie_target * 0.25 / 4:.0f}g, "
        f"Carbohydrates: {calorie_target * 0.50 / 4:.0f}g, "
        f"Fat: {calorie_target * 0.25 / 9:.0f}g\n\n"
        f"[USER REQUEST]\nGenerate a {days}-day meal plan. "
        f"{query}\n\n"
        "[RESPONSE]\n"
    )


# ── Agent 3 — Health Advisory ────────────────────────────────────────────────

HEALTH_ADVISORY_SYSTEM = (
    "[SYSTEM]\n"
    "You are a preventive nutrition guidance assistant. "
    "Your role is to provide general, evidence-based dietary guidance aligned to the user's "
    "health conditions. "
    "Always ground your response in the provided context. "
    "NEVER diagnose medical conditions. "
    "NEVER recommend specific medications or claim to replace a doctor. "
    "Provide general preventive nutrition information only. "
    "Be empathetic, practical, and specific to Indian dietary context where relevant.\n"
)

MEDICAL_DISCLAIMER = (
    "\n\n⚠️ IMPORTANT MEDICAL DISCLAIMER: This information is for general educational purposes "
    "only and is NOT medical advice. It does not replace the advice of a qualified physician, "
    "registered dietitian, or other healthcare professional. Always consult a healthcare "
    "provider before making significant dietary changes, especially if you have a medical "
    "condition or are taking medication."
)


def health_advisory_prompt(query: str, rag_context: str, profile: dict) -> str:
    return (
        f"{HEALTH_ADVISORY_SYSTEM}\n"
        f"[CONTEXT]\n{rag_context}\n\n"
        f"{_profile_section(profile)}\n"
        f"[USER REQUEST]\n{query}\n\n"
        "[RESPONSE]\n"
    )


# ── Agent 4 — Food Log & Feedback ────────────────────────────────────────────

FOOD_LOG_SYSTEM = (
    "[SYSTEM]\n"
    "You are a food logging and nutritional feedback assistant. "
    "Analyze the logged food item and provide: "
    "estimated nutritional values (calories, protein, carbohydrates, fat, fiber), "
    "strengths of the meal, practical improvements, and healthier alternatives. "
    "Ground your response in the provided context. "
    "Respond with a JSON object inside ```json ... ``` containing: "
    "calories, protein_g, carbs_g, fat_g, fiber_g, strengths (list), "
    "improvements (list), alternatives (list), feedback_message (string). "
    "Be motivational and factual. Never use diagnostic language.\n"
)


def food_log_prompt(
    food_name: str, quantity_g: float, rag_context: str, profile: Optional[dict] = None,
    daily_totals: Optional[dict] = None
) -> str:
    totals_text = ""
    if daily_totals:
        totals_text = (
            f"[TODAY'S TOTALS SO FAR]\n"
            f"Calories: {daily_totals.get('calories', 0):.0f} kcal, "
            f"Protein: {daily_totals.get('protein_g', 0):.1f}g, "
            f"Carbs: {daily_totals.get('carbs_g', 0):.1f}g, "
            f"Fat: {daily_totals.get('fat_g', 0):.1f}g\n\n"
        )
    return (
        f"{FOOD_LOG_SYSTEM}\n"
        f"[CONTEXT]\n{rag_context}\n\n"
        f"{_profile_section(profile)}\n"
        f"{totals_text}"
        f"[USER REQUEST]\nAnalyze: {quantity_g}g of {food_name}\n\n"
        "[RESPONSE]\n"
    )
