"""
Seed sample data — creates a demo user profile and sample food log entries.

Run from the project root:
    cd backend
    python ../scripts/seed_sample_data.py

Uses the demo profile defined in tests/fixtures/sample_profile.json.
"""

import sys
import json
import datetime
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR  = PROJECT_ROOT / "backend"
FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("seed_sample_data")


def main():
    from db.database import SessionLocal, init_db
    from db import crud

    logger.info("Initialising database …")
    init_db()

    # Load demo profile
    profile_path = FIXTURES_DIR / "sample_profile.json"
    with open(profile_path, encoding="utf-8") as f:
        profile = json.load(f)

    db = SessionLocal()
    try:
        user_id = profile["user_id"]

        # Upsert profile
        profile_data = {k: v for k, v in profile.items() if k != "user_id"}
        # Normalise list fields to strings
        if isinstance(profile_data.get("allergies"), list):
            profile_data["allergies"] = ", ".join(profile_data["allergies"])
        if isinstance(profile_data.get("health_conditions"), list):
            profile_data["health_conditions"] = ", ".join(profile_data["health_conditions"])
        crud.upsert_user(db, user_id, profile_data)
        logger.info("Demo profile created/updated for user_id=%s", user_id)

        # Seed sample food logs over the past 7 days
        sample_foods = [
            {"food_name": "Oats porridge with milk", "quantity_g": 200, "meal_type": "breakfast",
             "calories": 180, "protein_g": 8.0, "carbs_g": 32.0, "fat_g": 4.0, "fiber_g": 3.5},
            {"food_name": "Toor dal", "quantity_g": 150, "meal_type": "lunch",
             "calories": 174, "protein_g": 10.5, "carbs_g": 30.0, "fat_g": 0.6, "fiber_g": 7.5},
            {"food_name": "Whole wheat roti", "quantity_g": 80, "meal_type": "lunch",
             "calories": 238, "protein_g": 8.0, "carbs_g": 44.0, "fat_g": 4.0, "fiber_g": 4.4},
            {"food_name": "Mixed vegetable sabzi", "quantity_g": 150, "meal_type": "lunch",
             "calories": 120, "protein_g": 3.0, "carbs_g": 18.0, "fat_g": 4.0, "fiber_g": 4.0},
            {"food_name": "Brown rice", "quantity_g": 150, "meal_type": "dinner",
             "calories": 167, "protein_g": 3.9, "carbs_g": 34.5, "fat_g": 1.4, "fiber_g": 2.7},
            {"food_name": "Rajma curry", "quantity_g": 150, "meal_type": "dinner",
             "calories": 191, "protein_g": 13.1, "carbs_g": 34.2, "fat_g": 0.8, "fiber_g": 11.1},
            {"food_name": "Curd / yogurt", "quantity_g": 100, "meal_type": "evening_snack",
             "calories": 61, "protein_g": 3.5, "carbs_g": 4.7, "fat_g": 3.3, "fiber_g": 0.0},
        ]

        for i in range(7):
            day_offset = 6 - i
            log_time = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) - datetime.timedelta(days=day_offset)

            # Log a different subset each day for variety
            subset = sample_foods[i % len(sample_foods):(i % len(sample_foods)) + 3] + \
                     sample_foods[:(i % len(sample_foods))]
            subset = subset[:4]  # 4 items per day

            for food in subset:
                entry_data = dict(food)
                entry = crud.create_log_entry(db, user_id, entry_data)
                # Manually adjust timestamp for historical data
                from db.models import FoodLogEntry
                from sqlalchemy import update
                db.execute(
                    update(FoodLogEntry)
                    .where(FoodLogEntry.id == entry.id)
                    .values(logged_at=log_time)
                )
                db.commit()

        logger.info("Seeded 7 days of sample food log data for %s", user_id)
        logger.info("✅ Sample data seeded successfully.")
        logger.info("Start the backend and open the frontend to see your demo data.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
