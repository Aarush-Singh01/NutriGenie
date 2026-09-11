"""
Intent Classifier — maps request_type field or classifies free-text via keyword heuristics.

For a real watsonx Orchestrate deployment this module would call the Orchestrate
intent classification API. The local version uses rule-based keyword matching.
"""

from __future__ import annotations

import re

INTENT_MEAL_PLAN = "meal_plan"
INTENT_FOOD_LOG = "food_log"
INTENT_HEALTH_ADVICE = "health_advice"
INTENT_NUTRITION_QUERY = "nutrition_query"
INTENT_DASHBOARD = "dashboard"

_MEAL_PLAN_KEYWORDS = re.compile(
    r"\b(meal plan|diet plan|weekly plan|daily plan|generate plan|what (should|can) i eat|"
    r"plan my meals|food plan|nutrition plan)\b",
    re.IGNORECASE,
)
_FOOD_LOG_KEYWORDS = re.compile(
    r"\b(i (ate|had|consumed|eaten)|log(ged)?|track(ed)?|"
    r"calories in|how many calories|nutritional (value|info) of|analyze (my )?(meal|food))\b",
    re.IGNORECASE,
)
_HEALTH_ADVICE_KEYWORDS = re.compile(
    r"\b(diabetes|hypertension|heart disease|cholesterol|anemia|blood pressure|"
    r"blood sugar|health advice|health tip|preventive|chronic|condition|"
    r"should i avoid|is it safe for|can i eat with)\b",
    re.IGNORECASE,
)
_DASHBOARD_KEYWORDS = re.compile(
    r"\b(dashboard|progress|summary|how (am i doing|much have i eaten)|"
    r"today'?s (intake|calories)|weekly (trend|summary))\b",
    re.IGNORECASE,
)


def classify(message: str, explicit_type: str | None = None) -> str:
    """
    Return an intent string for the given message.

    Explicit request_type from the frontend takes precedence.
    Falls back to keyword heuristics.
    Health advice keywords are checked before meal-plan keywords because a message
    like "I have diabetes, what should I eat?" should route to health_advice.
    """
    if explicit_type and explicit_type in (
        INTENT_MEAL_PLAN,
        INTENT_FOOD_LOG,
        INTENT_HEALTH_ADVICE,
        INTENT_NUTRITION_QUERY,
        INTENT_DASHBOARD,
    ):
        return explicit_type

    # Health advice checked first — it's more specific than meal plan
    if _HEALTH_ADVICE_KEYWORDS.search(message):
        return INTENT_HEALTH_ADVICE
    if _FOOD_LOG_KEYWORDS.search(message):
        return INTENT_FOOD_LOG
    if _MEAL_PLAN_KEYWORDS.search(message):
        return INTENT_MEAL_PLAN
    if _DASHBOARD_KEYWORDS.search(message):
        return INTENT_DASHBOARD

    # Default: treat as a general nutrition knowledge query
    return INTENT_NUTRITION_QUERY
