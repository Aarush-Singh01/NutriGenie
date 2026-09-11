"""
FastAPI integration tests — uses a test SQLite DB and mocked Granite/RAG.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.database import get_db
from db.models import Base
from main import app


# ── Test database setup ──────────────────────────────────────────────────────

TEST_DB_URL = "sqlite:///./test_nutrigenie.db"

test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()
    # Clean up test DB file (ignore errors on Windows file locking)
    test_db_path = Path("./test_nutrigenie.db")
    try:
        if test_db_path.exists():
            test_db_path.unlink()
    except OSError:
        pass  # Windows may keep the file locked briefly; it will be overwritten next run


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


# ── Mocks ────────────────────────────────────────────────────────────────────

def mock_granite_generate(prompt, **kwargs):
    return "This is a mock nutrition response from the AI assistant."


def mock_rag_context(query, **kwargs):
    return "Toor dal contains approximately 116 kcal per 100g cooked, with 7g protein."


FOOD_LOG_JSON = '''```json
{
  "calories": 174,
  "protein_g": 10.5,
  "carbs_g": 30.0,
  "fat_g": 0.6,
  "fiber_g": 7.5,
  "strengths": ["High fiber", "Good protein"],
  "improvements": ["Add vegetables"],
  "alternatives": ["Moong dal"],
  "feedback_message": "Excellent choice! Dal is a nutritious staple."
}
```'''


# ── Health check ─────────────────────────────────────────────────────────────

class TestHealthCheck:
    def test_health_endpoint_returns_ok(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data

    def test_health_endpoint_has_service_field(self):
        response = client.get("/api/health")
        data = response.json()
        assert data["service"] == "NutriGenie API"


# ── Profile ──────────────────────────────────────────────────────────────────

class TestProfile:
    BASE_PROFILE = {
        "user_id": "api_test_user",
        "age": 30,
        "sex": "female",
        "height_cm": 162.0,
        "weight_kg": 58.0,
        "activity_level": "moderately_active",
        "primary_goal": "healthy_eating",
        "dietary_preference": "vegetarian",
        "allergies": ["gluten"],
        "health_conditions": [],
        "cuisine_preferences": "Indian",
    }

    def test_create_profile(self):
        response = client.post("/api/profile", json=self.BASE_PROFILE)
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "api_test_user"
        assert data["age"] == 30
        assert data["sex"] == "female"

    def test_get_profile(self):
        # Ensure profile exists first
        client.post("/api/profile", json=self.BASE_PROFILE)
        response = client.get("/api/profile/api_test_user")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "api_test_user"

    def test_get_nonexistent_profile_returns_404(self):
        response = client.get("/api/profile/nonexistent_xyz")
        assert response.status_code == 404

    def test_profile_validation_invalid_sex(self):
        bad = {**self.BASE_PROFILE, "sex": "alien", "user_id": "test_bad"}
        response = client.post("/api/profile", json=bad)
        assert response.status_code == 422

    def test_profile_validation_age_out_of_range(self):
        bad = {**self.BASE_PROFILE, "age": 0, "user_id": "test_bad2"}
        response = client.post("/api/profile", json=bad)
        assert response.status_code == 422


# ── Food Log ─────────────────────────────────────────────────────────────────

class TestFoodLog:
    USER_ID = "log_test_user"

    @pytest.fixture(autouse=True)
    def setup_profile(self):
        client.post("/api/profile", json={
            "user_id": self.USER_ID, "age": 28, "sex": "male",
            "height_cm": 172.0, "weight_kg": 70.0,
            "activity_level": "lightly_active", "primary_goal": "maintenance",
            "dietary_preference": "none", "allergies": [], "health_conditions": [],
            "cuisine_preferences": "Indian",
        })

    def test_log_food_entry(self):
        with patch("ai.granite_client.generate", return_value=FOOD_LOG_JSON), \
             patch("rag.retriever.retrieve_as_context", return_value=mock_rag_context("")):
            response = client.post("/api/log", json={
                "user_id": self.USER_ID,
                "food_name": "toor dal",
                "quantity": 150,
                "unit": "g",
                "meal_type": "lunch",
            })
        assert response.status_code == 200
        data = response.json()
        assert "entry_id" in data
        assert data["food_name"] == "toor dal"
        assert "nutrition" in data

    def test_today_log_returns_structure(self):
        response = client.get(f"/api/log/today?user_id={self.USER_ID}")
        assert response.status_code == 200
        data = response.json()
        assert "entries" in data
        assert "daily_totals" in data
        assert "calorie_target" in data

    def test_log_validation_missing_food_name(self):
        response = client.post("/api/log", json={
            "user_id": self.USER_ID,
            "quantity": 100,
            "unit": "g",
        })
        assert response.status_code == 422


# ── Dashboard ────────────────────────────────────────────────────────────────

class TestDashboard:
    USER_ID = "dash_test_user"

    @pytest.fixture(autouse=True)
    def setup_profile(self):
        client.post("/api/profile", json={
            "user_id": self.USER_ID, "age": 35, "sex": "female",
            "height_cm": 160.0, "weight_kg": 62.0,
            "activity_level": "moderately_active", "primary_goal": "weight_loss",
            "dietary_preference": "vegetarian", "allergies": [], "health_conditions": [],
            "cuisine_preferences": "Indian",
        })

    def test_daily_dashboard(self):
        response = client.get(f"/api/dashboard/daily?user_id={self.USER_ID}")
        assert response.status_code == 200
        data = response.json()
        assert "calorie_consumed" in data
        assert "calorie_target" in data
        assert "nutrients" in data
        assert len(data["nutrients"]) > 0

    def test_weekly_dashboard(self):
        response = client.get(f"/api/dashboard/weekly?user_id={self.USER_ID}")
        assert response.status_code == 200
        data = response.json()
        assert "weekly_data" in data
        assert len(data["weekly_data"]) == 7


# ── Chat ─────────────────────────────────────────────────────────────────────

class TestChat:
    USER_ID = "chat_test_user"

    @pytest.fixture(autouse=True)
    def setup_profile(self):
        client.post("/api/profile", json={
            "user_id": self.USER_ID, "age": 25, "sex": "male",
            "height_cm": 175.0, "weight_kg": 70.0,
            "activity_level": "moderately_active", "primary_goal": "healthy_eating",
            "dietary_preference": "vegetarian", "allergies": [], "health_conditions": [],
            "cuisine_preferences": "Indian",
        })

    def test_chat_nutrition_query(self):
        with patch("ai.granite_client.generate", return_value=mock_granite_generate("")), \
             patch("rag.retriever.retrieve_as_context", return_value=mock_rag_context("")):
            response = client.post("/api/chat", json={
                "user_id": self.USER_ID,
                "message": "How much protein is in 100g of paneer?",
                "request_type": "nutrition_query",
            })
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "agent_used" in data

    def test_chat_validation_empty_message(self):
        response = client.post("/api/chat", json={
            "user_id": self.USER_ID,
            "message": "",
        })
        assert response.status_code == 422
