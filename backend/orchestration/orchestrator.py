"""
AgentOrchestrator — local router for NutriGenie agents.

This class is a drop-in replacement for watsonx Orchestrate.
The routing logic mirrors what would be configured as Orchestrate Skills;
replacing the local dispatcher with the real API call is a single-function swap
(see `_call_watsonx_orchestrate` stub at the bottom of this file).

Controlled by USE_LOCAL_ORCHESTRATOR env var:
  true  → use this local router (default for development)
  false → call the real watsonx Orchestrate REST API
"""

from __future__ import annotations

import logging
from typing import Optional

import requests

from config import settings
from orchestration.intent_classifier import (
    classify,
    INTENT_MEAL_PLAN,
    INTENT_FOOD_LOG,
    INTENT_HEALTH_ADVICE,
    INTENT_NUTRITION_QUERY,
    INTENT_DASHBOARD,
)
from agents.knowledge_agent import KnowledgeAgent
from agents.food_log_agent import FoodLogAgent
from agents.recommendation_agent import RecommendationAgent
from agents.health_advisory_agent import HealthAdvisoryAgent

logger = logging.getLogger(__name__)

# Agent singletons (created once per process)
_knowledge_agent = KnowledgeAgent()
_food_log_agent = FoodLogAgent()
_recommendation_agent = RecommendationAgent()
_health_advisory_agent = HealthAdvisoryAgent()


class AgentOrchestrator:
    """
    Local multi-agent router — structurally identical to watsonx Orchestrate skills routing.
    """

    def dispatch(
        self,
        message: str,
        profile: Optional[dict] = None,
        request_type: Optional[str] = None,
        food_name: Optional[str] = None,
        quantity_g: Optional[float] = None,
        daily_totals: Optional[dict] = None,
        plan_days: int = 1,
    ) -> dict:
        """
        Classify intent and dispatch to the appropriate agent.

        Returns a unified response dict with keys:
          response, agent_used, disclaimer (optional), extra data.
        """
        if not settings.use_local_orchestrator:
            return _call_watsonx_orchestrate(
                message, profile, request_type, food_name, quantity_g, plan_days
            )

        intent = classify(message, explicit_type=request_type)
        logger.info("Orchestrator intent: %s | message: %.60s", intent, message)

        if intent == INTENT_FOOD_LOG and food_name:
            result = _food_log_agent.analyze(
                food_name=food_name,
                quantity_g=quantity_g or 100.0,
                profile=profile,
                daily_totals=daily_totals,
            )
            return {
                "response": result.get("feedback", ""),
                "agent_used": result["agent"],
                "nutrition": {
                    "calories": result["calories"],
                    "protein_g": result["protein_g"],
                    "carbs_g": result["carbs_g"],
                    "fat_g": result["fat_g"],
                    "fiber_g": result["fiber_g"],
                },
                "strengths": result.get("strengths", []),
                "improvements": result.get("improvements", []),
                "alternatives": result.get("alternatives", []),
            }

        if intent == INTENT_MEAL_PLAN:
            result = _recommendation_agent.generate_plan(
                profile=profile or {},
                days=plan_days,
                extra_query=message,
            )
            response_text = result.get("raw_response", "")

            # If profile has health conditions, get advisory note too
            disclaimer = None
            if profile and profile.get("health_conditions") not in (None, "", "none"):
                advisory = _health_advisory_agent.advise(
                    query=f"Review this meal plan for someone with {profile.get('health_conditions')}",
                    profile=profile,
                )
                response_text += f"\n\n--- Health Advisory ---\n{advisory['response']}"
                disclaimer = advisory["disclaimer"]

            return {
                "response": response_text,
                "agent_used": result["agent"],
                "calorie_target": result["calorie_target"],
                "days": result["days"],
                "disclaimer": disclaimer,
            }

        if intent == INTENT_HEALTH_ADVICE:
            result = _health_advisory_agent.advise(
                query=message, profile=profile or {}
            )
            return {
                "response": result["response"],
                "agent_used": result["agent"],
                "disclaimer": result["disclaimer"],
            }

        if intent == INTENT_DASHBOARD:
            return {
                "response": "Please check the Dashboard tab for your nutrition summary and charts.",
                "agent_used": "orchestrator",
            }

        # Default: nutrition knowledge query
        result = _knowledge_agent.answer(query=message, profile=profile)
        return {
            "response": result["response"],
            "agent_used": result["agent"],
        }


def _call_watsonx_orchestrate(
    message: str,
    profile: Optional[dict],
    request_type: Optional[str],
    food_name: Optional[str],
    quantity_g: Optional[float],
    plan_days: int,
) -> dict:
    """
    Stub for real watsonx Orchestrate API call.
    Replace the body of this function with the actual Orchestrate REST call
    when moving to production. The interface (parameters + return dict) is
    identical to the local orchestrator.
    """
    if not settings.watsonx_orchestrate_url or not settings.watsonx_orchestrate_instance_id:
        logger.warning(
            "watsonx Orchestrate credentials not configured. Falling back to local orchestrator."
        )
        # Fall back gracefully
        settings.use_local_orchestrator = True
        orchestrator = AgentOrchestrator()
        return orchestrator.dispatch(
            message, profile, request_type, food_name, quantity_g, None, plan_days
        )

    # TODO: Implement actual watsonx Orchestrate API call here.
    raise NotImplementedError("watsonx Orchestrate integration not yet implemented in this build.")


# Module-level singleton
orchestrator = AgentOrchestrator()
