"""
RAG Ingestor — loads raw knowledge base data, chunks it, embeds it, and stores in ChromaDB.
Chunk size: 512 tokens (≈2048 chars), 50-token (≈200 char) overlap.
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import List, Tuple

from sentence_transformers import SentenceTransformer

from rag.chroma_client import get_chroma_client, get_or_create_collection

logger = logging.getLogger(__name__)

CHUNK_SIZE = 2048    # ~512 tokens
CHUNK_OVERLAP = 200  # ~50 tokens


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping chunks."""
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def _load_json_foods(json_path: Path) -> List[Tuple[str, str]]:
    """Load nutrition_knowledge.json and convert each food entry to a text chunk."""
    docs: List[Tuple[str, str]] = []
    with open(json_path, encoding="utf-8") as f:
        foods = json.load(f)

    for food in foods:
        name = food.get("name", "Unknown")
        category = food.get("category", "")
        per_key = "per_100g" if "per_100g" in food else "per_100ml"
        nutrients = food.get(per_key, {})
        notes = food.get("notes", "")
        tags = ", ".join(food.get("tags", []))

        lines = [f"Food: {name}", f"Category: {category}", f"Nutritional info ({per_key}):"]
        for nutrient, value in nutrients.items():
            if isinstance(value, (int, float)):
                lines.append(f"  {nutrient}: {value}")
        if notes:
            lines.append(f"Notes: {notes}")
        if tags:
            lines.append(f"Tags: {tags}")

        text = "\n".join(lines)
        source = f"nutrition_knowledge/{food.get('id', name)}"
        docs.append((text, source))

    return docs


def _load_markdown(md_path: Path) -> List[Tuple[str, str]]:
    """Load a Markdown file and return chunked (text, source) pairs."""
    with open(md_path, encoding="utf-8") as f:
        content = f.read()

    # Split by double newline to preserve section structure before chunking
    paragraphs = re.split(r"\n{2,}", content)
    assembled = ""
    docs: List[Tuple[str, str]] = []
    source = str(md_path.name)

    for para in paragraphs:
        if len(assembled) + len(para) + 2 > CHUNK_SIZE:
            if assembled.strip():
                docs.append((assembled.strip(), source))
            assembled = para
        else:
            assembled += "\n\n" + para if assembled else para

    if assembled.strip():
        docs.append((assembled.strip(), source))

    return docs


def ingest_all(data_dir: Path) -> int:
    """
    Ingest all knowledge base files into ChromaDB.
    Returns the total number of chunks stored.
    """
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    client = get_chroma_client()
    collection = get_or_create_collection(client)

    # Clear existing data before re-ingestion
    existing_ids = collection.get(include=[])["ids"]
    if existing_ids:
        collection.delete(ids=existing_ids)
        logger.info("Cleared %d existing chunks from ChromaDB.", len(existing_ids))

    all_docs: List[Tuple[str, str]] = []

    # Load main nutrition JSON
    json_path = data_dir / "nutrition_knowledge.json"
    if json_path.exists():
        docs = _load_json_foods(json_path)
        logger.info("Loaded %d food entries from %s", len(docs), json_path)
        all_docs.extend(docs)

    # Load Markdown files recursively from data/raw/
    raw_dir = data_dir / "raw"
    if raw_dir.exists():
        for md_file in raw_dir.rglob("*.md"):
            docs = _load_markdown(md_file)
            logger.info("Loaded %d chunks from %s", len(docs), md_file)
            all_docs.extend(docs)

    if not all_docs:
        logger.warning("No documents found to ingest!")
        return 0

    # Embed and store in batches
    batch_size = 64
    total_stored = 0
    for i in range(0, len(all_docs), batch_size):
        batch = all_docs[i : i + batch_size]
        texts = [doc[0] for doc in batch]
        sources = [doc[1] for doc in batch]
        ids = [f"doc_{i + j}" for j in range(len(batch))]

        embeddings = model.encode(texts).tolist()
        collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=[{"source": s} for s in sources],
            ids=ids,
        )
        total_stored += len(batch)
        logger.info("Stored batch %d-%d (%d total so far)", i, i + len(batch), total_stored)

    logger.info("Ingestion complete. Total chunks in ChromaDB: %d", total_stored)
    return total_stored
