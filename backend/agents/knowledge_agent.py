"""Nutrition Knowledge Agent — answers factual nutrition questions using RAG + Granite."""

from __future__ import annotations

import logging
from typing import Optional

from agents.base_agent import BaseAgent
from ai.prompt_templates import knowledge_prompt

logger = logging.getLogger(__name__)


class KnowledgeAgent(BaseAgent):
    agent_name = "nutrition_knowledge"

    def answer(self, query: str, profile: Optional[dict] = None) -> dict:
        """
        Answer a nutrition question grounded in the RAG knowledge base.

        Returns:
            {
                "response": str,
                "agent": str,
                "sources_found": bool,
            }
        """
        context = self._retrieve_context(query, top_k=5)
        sources_found = not context.startswith("No specific data")

        prompt = knowledge_prompt(query, context, profile)
        response = self._generate(prompt)

        return {
            "response": response,
            "agent": self.agent_name,
            "sources_found": sources_found,
        }
