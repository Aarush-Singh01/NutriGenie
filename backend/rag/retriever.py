"""
RAG Retriever — queries ChromaDB and returns top-k relevant chunks.

Uses sentence-transformers locally so no API key is needed for embeddings.
"""

import logging
from typing import List, Dict, Any, Optional

from sentence_transformers import SentenceTransformer

from rag.chroma_client import get_chroma_client, get_or_create_collection

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 0.5  # Do not return chunks below this cosine similarity

_embedding_model: Optional[SentenceTransformer] = None


def _get_embedding_model() -> SentenceTransformer:
    """Lazy-load the embedding model (shared singleton)."""
    global _embedding_model
    if _embedding_model is None:
        logger.info("Loading sentence-transformers model (first call — may take a moment)…")
        _embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        logger.info("Embedding model loaded.")
    return _embedding_model


def retrieve(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Embed the query and return the top-k most similar knowledge chunks.

    Returns a list of dicts with keys: 'text', 'source', 'score'.
    If the collection is empty or all scores are below threshold, returns [].
    """
    try:
        model = _get_embedding_model()
        query_embedding = model.encode(query).tolist()

        client = get_chroma_client()
        collection = get_or_create_collection(client)

        count = collection.count()
        if count == 0:
            logger.warning("ChromaDB collection is empty. Run the ingestion script first.")
            return []

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, count),
            include=["documents", "metadatas", "distances"],
        )

        chunks: List[Dict[str, Any]] = []
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for doc, meta, dist in zip(documents, metadatas, distances):
            # ChromaDB with cosine space returns distance (0=identical, 2=opposite).
            # Convert to similarity: similarity = 1 - distance/2
            similarity = 1.0 - (dist / 2.0)
            if similarity >= SIMILARITY_THRESHOLD:
                chunks.append(
                    {
                        "text": doc,
                        "source": meta.get("source", "unknown"),
                        "score": round(similarity, 3),
                    }
                )

        logger.debug("RAG retrieved %d chunks for query: %s", len(chunks), query[:60])
        return chunks

    except Exception as exc:
        logger.error("RAG retrieval error: %s", exc)
        return []


def retrieve_as_context(query: str, top_k: int = 5, max_tokens: int = 2000) -> str:
    """
    Convenience wrapper — returns retrieved chunks concatenated as a single
    context string suitable for injection into a Granite prompt.
    """
    chunks = retrieve(query, top_k=top_k)
    if not chunks:
        return "No specific data found in the knowledge base for this query."

    parts = []
    total_chars = 0
    char_budget = max_tokens * 4  # rough chars-per-token approximation

    for chunk in chunks:
        text = chunk["text"]
        if total_chars + len(text) > char_budget:
            remaining = char_budget - total_chars
            if remaining > 100:
                parts.append(text[:remaining] + "…")
            break
        parts.append(text)
        total_chars += len(text)

    return "\n\n---\n\n".join(parts)
