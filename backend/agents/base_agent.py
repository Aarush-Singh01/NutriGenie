"""
Base agent class — wires Granite + RAG for all NutriGenie agents.

Agent subclasses must not import GraniteClient or RAGRetriever directly;
they inherit shared access via this base class.
"""

from __future__ import annotations

import logging
from typing import Optional

from ai import granite_client
from ai.prompt_templates import MEDICAL_DISCLAIMER
from rag.retriever import retrieve_as_context

logger = logging.getLogger(__name__)


class BaseAgent:
    """Shared foundation for all NutriGenie agents."""

    agent_name: str = "base"

    def _retrieve_context(self, query: str, top_k: int = 5) -> str:
        """Retrieve RAG context for the given query."""
        return retrieve_as_context(query, top_k=top_k)

    def _generate(self, prompt: str, max_new_tokens: int = 1000) -> str:
        """Call Granite and return generated text."""
        return granite_client.generate(prompt, max_new_tokens=max_new_tokens)

    def _append_disclaimer(self, text: str) -> str:
        """Append the mandatory medical disclaimer to a health-advisory response."""
        return text + MEDICAL_DISCLAIMER

    def _is_fallback(self, text: str) -> bool:
        """Return True if the response is a fallback (not a real Granite response)."""
        return text.startswith("[FALLBACK")
