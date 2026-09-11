"""ChromaDB client setup for NutriGenie RAG."""

import logging
import os
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings

from config import settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "nutrition_knowledge"


def get_chroma_client() -> chromadb.PersistentClient:
    """Return a persistent ChromaDB client pointing to the configured path."""
    db_path = Path(settings.chroma_db_path).resolve()
    db_path.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(
        path=str(db_path),
        settings=ChromaSettings(anonymized_telemetry=False),
    )
    return client


def get_or_create_collection(client: chromadb.PersistentClient) -> chromadb.Collection:
    """Return the nutrition knowledge collection, creating it if absent."""
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
