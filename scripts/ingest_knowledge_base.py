"""
One-time RAG ingestion script.

Run from the project root:
    cd backend
    python ../scripts/ingest_knowledge_base.py

This populates data/chroma_db/ which is gitignored and must exist before
starting the backend for the first time.
"""

import sys
import logging
from pathlib import Path

# ── Path setup (runs from project root or scripts/ dir) ─────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR  = PROJECT_ROOT / "backend"
DATA_DIR     = PROJECT_ROOT / "data"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ingest_knowledge_base")


def main():
    logger.info("=" * 60)
    logger.info("NutriGenie — Knowledge Base Ingestion")
    logger.info("=" * 60)
    logger.info("Data directory : %s", DATA_DIR)

    # Import after path setup so config/settings load from .env correctly
    from rag.ingestor import ingest_all

    total = ingest_all(DATA_DIR)

    if total == 0:
        logger.error("No documents were ingested. Check that data/ files exist.")
        sys.exit(1)

    logger.info("=" * 60)
    logger.info("✅ Ingestion complete. %d chunks stored in ChromaDB.", total)
    logger.info("ChromaDB path: %s", DATA_DIR / "chroma_db")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
