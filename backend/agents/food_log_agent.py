"""
Food Log & Feedback Agent.

Accepts a food entry, looks up nutritional data via RAG, calls Granite for
structured feedback, and returns parsed nutritional values + coaching message.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Optional

from agents.base_agent import BaseAgent
from ai.prompt_templates import food_log_prompt

logger = logging.getLogger(__name__)


class FoodLogAgent(BaseAgent):
    agent_name = "food_log"

    def analyze(
        self,
        food_name: str,
        quantity_g: float,
        profile: Optional[dict] = None,
        daily_totals: Optional[dict] = None,
    ) -> dict:
        """
        Analyze a logged food item.

        Returns:
            {
                "calories": float,
                "protein_g": float,
                "carbs_g": float,
                "fat_g": float,
                "fiber_g": float,
                "feedback": str,
                "strengths": list,
                "improvements": list,
                "alternatives": list,
                "agent": str,
            }
        """
        query = f"{food_name} nutritional information per {quantity_g}g"
        context = self._retrieve_context(query, top_k=5)

        prompt = food_log_prompt(food_name, quantity_g, context, profile, daily_totals)
        raw = self._generate(prompt)

        if self._is_fallback(raw):
            # Return estimated values from knowledge base parsing when Granite unavailable
            return self._estimate_from_context(food_name, quantity_g, context, raw)

        return self._parse_llm_response(raw, food_name, quantity_g)

    def _parse_llm_response(self, raw: str, food_name: str, quantity_g: float) -> dict:
        """Extract JSON from LLM response, falling back to defaults on parse error."""
        # Try to extract JSON block
        match = re.search(r"```json\s*(.*?)\s*```", raw, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            # Try to find raw JSON object
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            json_str = match.group(0) if match else None

        if json_str:
            try:
                data = json.loads(json_str)
                return {
                    "calories": float(data.get("calories", 0)),
                    "protein_g": float(data.get("protein_g", 0)),
                    "carbs_g": float(data.get("carbs_g", 0)),
                    "fat_g": float(data.get("fat_g", 0)),
                    "fiber_g": float(data.get("fiber_g", 0)),
                    "feedback": data.get("feedback_message", raw[:300]),
                    "strengths": data.get("strengths", []),
                    "improvements": data.get("improvements", []),
                    "alternatives": data.get("alternatives", []),
                    "agent": self.agent_name,
                }
            except (json.JSONDecodeError, ValueError) as exc:
                logger.warning("Failed to parse LLM JSON for %s: %s", food_name, exc)

        # Fallback: return the raw text as feedback with zero nutrition
        return {
            "calories": 0.0,
            "protein_g": 0.0,
            "carbs_g": 0.0,
            "fat_g": 0.0,
            "fiber_g": 0.0,
            "feedback": raw[:500] if raw else "Unable to analyze this food item.",
            "strengths": [],
            "improvements": [],
            "alternatives": [],
            "agent": self.agent_name,
        }

    def _estimate_from_context(
        self, food_name: str, quantity_g: float, context: str, fallback_msg: str
    ) -> dict:
        """Very rough estimate when Granite is unavailable — parses RAG text for numbers."""
        # Simple pattern matching on context for calorie values
        calories = 0.0
        protein_g = 0.0
        carbs_g = 0.0
        fat_g = 0.0
        fiber_g = 0.0

        if context and not context.startswith("No specific"):
            cal_match = re.search(r"calories[:\s]+(\d+\.?\d*)", context, re.IGNORECASE)
            prot_match = re.search(r"protein_g[:\s]+(\d+\.?\d*)", context, re.IGNORECASE)
            carb_match = re.search(r"carbs_g[:\s]+(\d+\.?\d*)", context, re.IGNORECASE)
            fat_match = re.search(r"fat_g[:\s]+(\d+\.?\d*)", context, re.IGNORECASE)
            fiber_match = re.search(r"fiber_g[:\s]+(\d+\.?\d*)", context, re.IGNORECASE)

            scale = quantity_g / 100.0
            if cal_match:
                calories = float(cal_match.group(1)) * scale
            if prot_match:
                protein_g = float(prot_match.group(1)) * scale
            if carb_match:
                carbs_g = float(carb_match.group(1)) * scale
            if fat_match:
                fat_g = float(fat_match.group(1)) * scale
            if fiber_match:
                fiber_g = float(fiber_match.group(1)) * scale

        return {
            "calories": round(calories, 1),
            "protein_g": round(protein_g, 1),
            "carbs_g": round(carbs_g, 1),
            "fat_g": round(fat_g, 1),
            "fiber_g": round(fiber_g, 1),
            "feedback": fallback_msg,
            "strengths": [],
            "improvements": ["AI service unavailable — values are estimated from knowledge base."],
            "alternatives": [],
            "agent": self.agent_name,
        }
