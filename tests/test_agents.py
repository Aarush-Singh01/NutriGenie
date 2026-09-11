"""
Tests for NutriGenie agents — uses mocked Granite and RAG.
Verifies output schema and mandatory disclaimer presence.
"""

import sys
from pathlib import Path

# Ensure backend is on the path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import pytest
from unittest.mock import patch, MagicMock


SAMPLE_PROFILE = {
    "user_id": "test_user_001",
    "age": 42,
    "sex": "male",
    "height_cm": 175.0,
    "weight_kg": 82.0,
    "activity_level": "moderately_active",
    "primary_goal": "weight_loss",
    "dietary_preference": "vegetarian",
    "allergies": "peanuts",
    "health_conditions": "diabetes, hypertension",
    "cuisine_preferences": "Indian",
}


# ── Helper to mock both Granite and RAG ──────────────────────────────────────

def _mock_granite(return_value: str):
    return patch("ai.granite_client.generate", return_value=return_value)


def _mock_rag(return_value: str = "Brown rice contains 111 kcal per 100g."):
    return patch("rag.retriever.retrieve_as_context", return_value=return_value)


# ── Nutrition Knowledge Agent ────────────────────────────────────────────────

class TestKnowledgeAgent:
    def test_answer_returns_response_and_agent_name(self):
        from agents.knowledge_agent import KnowledgeAgent
        agent = KnowledgeAgent()

        with _mock_granite("Brown rice has 111 kcal per 100g cooked."), _mock_rag():
            result = agent.answer("How many calories in brown rice?", SAMPLE_PROFILE)

        assert "response" in result
        assert result["agent"] == "nutrition_knowledge"
        assert len(result["response"]) > 0

    def test_answer_with_no_profile(self):
        from agents.knowledge_agent import KnowledgeAgent
        agent = KnowledgeAgent()

        with _mock_granite("General nutrition info."), _mock_rag():
            result = agent.answer("What is protein?")

        assert result["agent"] == "nutrition_knowledge"
        assert "response" in result


# ── Food Log Agent ───────────────────────────────────────────────────────────

class TestFoodLogAgent:
    def _make_json_response(self):
        return '''```json
{
  "calories": 165,
  "protein_g": 12.5,
  "carbs_g": 28.0,
  "fat_g": 1.8,
  "fiber_g": 4.5,
  "strengths": ["Good source of protein", "High fiber"],
  "improvements": ["Add a protein source"],
  "alternatives": ["Moong dal chilla"],
  "feedback_message": "Great choice! Dal is an excellent plant protein source."
}
```'''

    def test_analyze_returns_nutrition_keys(self):
        from agents.food_log_agent import FoodLogAgent
        agent = FoodLogAgent()

        with _mock_granite(self._make_json_response()), _mock_rag():
            result = agent.analyze("toor dal", 150.0, SAMPLE_PROFILE)

        for key in ["calories", "protein_g", "carbs_g", "fat_g", "fiber_g", "feedback", "agent"]:
            assert key in result, f"Missing key: {key}"
        assert result["agent"] == "food_log"
        assert result["calories"] == pytest.approx(165, abs=1)

    def test_analyze_fallback_when_granite_unavailable(self):
        from agents.food_log_agent import FoodLogAgent
        agent = FoodLogAgent()

        fallback = "[FALLBACK — AI service unavailable: No credentials]\n\nGeneral info."
        with _mock_granite(fallback), _mock_rag("calories: 130\nprotein_g: 2.7"):
            result = agent.analyze("white rice", 100.0)

        assert "calories" in result
        assert result["agent"] == "food_log"


# ── Diet Recommendation Agent ────────────────────────────────────────────────

class TestRecommendationAgent:
    def test_compute_calorie_target_male_moderately_active(self):
        from agents.recommendation_agent import compute_calorie_target
        profile = {
            "sex": "male", "age": 30, "weight_kg": 70, "height_cm": 175,
            "activity_level": "moderately_active", "primary_goal": "maintenance",
        }
        target = compute_calorie_target(profile)
        # Mifflin-St Jeor: BMR = 10*70 + 6.25*175 - 5*30 + 5 = 1693.75 * 1.55 = 2625.3
        assert 2400 < target < 2900

    def test_compute_calorie_target_weight_loss(self):
        from agents.recommendation_agent import compute_calorie_target
        profile = {
            "sex": "female", "age": 28, "weight_kg": 60, "height_cm": 162,
            "activity_level": "lightly_active", "primary_goal": "weight_loss",
        }
        maintenance = compute_calorie_target({**profile, "primary_goal": "maintenance"})
        loss = compute_calorie_target(profile)
        assert loss == pytest.approx(maintenance - 500, abs=1)

    def test_generate_plan_returns_days(self):
        from agents.recommendation_agent import RecommendationAgent
        agent = RecommendationAgent()

        granite_response = '[FALLBACK — AI service unavailable: test]'
        with _mock_granite(granite_response), _mock_rag():
            result = agent.generate_plan(SAMPLE_PROFILE, days=1)

        assert "days" in result
        assert "calorie_target" in result
        assert len(result["days"]) == 1
        day = result["days"][0]
        assert "breakfast" in day
        assert "lunch" in day
        assert "dinner" in day


# ── Health Advisory Agent ────────────────────────────────────────────────────

class TestHealthAdvisoryAgent:
    def test_disclaimer_always_present(self):
        """Disclaimer must be present in EVERY response — hard safety requirement."""
        from agents.health_advisory_agent import HealthAdvisoryAgent
        agent = HealthAdvisoryAgent()

        with _mock_granite("Increase fiber intake to help manage blood sugar."), _mock_rag():
            result = agent.advise("What should I eat for diabetes?", SAMPLE_PROFILE)

        assert "disclaimer" in result
        assert result["disclaimer"] is not None
        assert len(result["disclaimer"]) > 10

    def test_disclaimer_present_when_granite_fails(self):
        """Disclaimer must be present even when Granite returns a fallback."""
        from agents.health_advisory_agent import HealthAdvisoryAgent
        agent = HealthAdvisoryAgent()

        fallback = "[FALLBACK — AI service unavailable: No credentials]"
        with _mock_granite(fallback), _mock_rag():
            result = agent.advise("Health advice", SAMPLE_PROFILE)

        assert result["disclaimer"] is not None
        assert "not medical advice" in result["disclaimer"].lower() or \
               "medical" in result["disclaimer"].lower()

    def test_never_diagnose_in_prompt(self):
        """Verify the health advisory prompt explicitly forbids diagnosis."""
        from ai.prompt_templates import health_advisory_prompt
        prompt = health_advisory_prompt("test query", "test context", SAMPLE_PROFILE)
        assert "NEVER diagnose" in prompt or "Never diagnose" in prompt


# ── Orchestrator Intent Classification ──────────────────────────────────────

class TestIntentClassifier:
    def test_explicit_type_takes_precedence(self):
        from orchestration.intent_classifier import classify
        intent = classify("some random message", explicit_type="meal_plan")
        assert intent == "meal_plan"

    def test_meal_plan_keywords(self):
        from orchestration.intent_classifier import classify, INTENT_MEAL_PLAN
        assert classify("Generate a meal plan for me") == INTENT_MEAL_PLAN
        assert classify("what should i eat today") == INTENT_MEAL_PLAN

    def test_health_advice_keywords(self):
        from orchestration.intent_classifier import classify, INTENT_HEALTH_ADVICE
        assert classify("I have diabetes, what should I eat?") == INTENT_HEALTH_ADVICE
        assert classify("tips for hypertension") == INTENT_HEALTH_ADVICE

    def test_food_log_keywords(self):
        from orchestration.intent_classifier import classify, INTENT_FOOD_LOG
        assert classify("I ate brown rice for lunch") == INTENT_FOOD_LOG
        assert classify("calories in my breakfast") == INTENT_FOOD_LOG

    def test_default_is_nutrition_query(self):
        from orchestration.intent_classifier import classify, INTENT_NUTRITION_QUERY
        assert classify("What is vitamin B12?") == INTENT_NUTRITION_QUERY
