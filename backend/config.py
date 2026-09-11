"""
NutriGenie configuration — all settings loaded from environment variables.
Uses pydantic-settings so that values can be overridden via .env or real env vars.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # ── IBM watsonx.ai ──────────────────────────────────────────────────────
    watsonx_api_key: str = Field(default="", alias="WATSONX_API_KEY")
    watsonx_project_id: str = Field(default="", alias="WATSONX_PROJECT_ID")
    watsonx_url: str = Field(
        default="https://us-south.ml.cloud.ibm.com", alias="WATSONX_URL"
    )
    watsonx_model_id: str = Field(
        default="ibm/granite-13b-instruct-v2", alias="WATSONX_MODEL_ID"
    )

    # ── IBM watsonx Orchestrate ─────────────────────────────────────────────
    watsonx_orchestrate_url: str = Field(
        default="", alias="WATSONX_ORCHESTRATE_URL"
    )
    watsonx_orchestrate_instance_id: str = Field(
        default="", alias="WATSONX_ORCHESTRATE_INSTANCE_ID"
    )

    # ── Orchestration mode ──────────────────────────────────────────────────
    # Set USE_LOCAL_ORCHESTRATOR=true (default) to use the local AgentOrchestrator.
    # Set to false when a real watsonx Orchestrate instance is available.
    use_local_orchestrator: bool = Field(
        default=True, alias="USE_LOCAL_ORCHESTRATOR"
    )

    # ── Database ────────────────────────────────────────────────────────────
    database_url: str = Field(
        default="sqlite:///./nutrigenie.db", alias="DATABASE_URL"
    )

    # ── ChromaDB ────────────────────────────────────────────────────────────
    chroma_db_path: str = Field(
        default="../data/chroma_db", alias="CHROMA_DB_PATH"
    )

    # ── FastAPI / Security ──────────────────────────────────────────────────
    secret_key: str = Field(
        default="dev_secret_change_in_production", alias="SECRET_KEY"
    )
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000", "null"],
        alias="CORS_ORIGINS",
    )

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "populate_by_name": True}


# Singleton instance — import this from all modules.
settings = Settings()
