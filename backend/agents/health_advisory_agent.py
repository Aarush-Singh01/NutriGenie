"""
Health Advisory Agent.

Provides preventive nutrition guidance grounded in RAG.
Disclaimer injection happens in Python code AFTER the LLM call returns —
this is a hard safety requirement ensuring the disclaimer is never omitted.
"""

from __future__ import annotations

import logging
from typing import Optional

from agents.base_agent import BaseAgent
from ai.prompt_templates import health_advisory_prompt

logger = logging.getLogger(__name__)


class HealthAdvisoryAgent(BaseAgent):
    agent_name = "health_advisory"

    def advise(self, query: str, profile: dict) -> dict:
        """
        Generate health advisory response with mandatory disclaimer.

        The disclaimer is ALWAYS appended programmatically in Python,
        not inside the prompt or LLM output — safety requirement.

        Returns:
            {
                "response": str,       # advice text
                "disclaimer": str,     # always present
                "agent": str,
            }
        """
        health_conds = profile.get("health_conditions", "none")
        rag_query = f"nutrition guidance {health_conds} {query}"
        context = self._retrieve_context(rag_query, top_k=5)

        prompt = health_advisory_prompt(query, context, profile)
        llm_response = self._generate(prompt)

        # MANDATORY: Disclaimer injected here programmatically, never by LLM.
        from ai.prompt_templates import MEDICAL_DISCLAIMER
        disclaimer = MEDICAL_DISCLAIMER.strip()

        return {
            "response": llm_response,
            "disclaimer": disclaimer,
            "agent": self.agent_name,
        }
