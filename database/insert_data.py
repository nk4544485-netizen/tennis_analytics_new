import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from connection import get_connection
from api.sport_radar import fetch_sport_radar_data


try:
    categories, competitions = fetch_sport_radar_data()
except RuntimeError as exc:
    raise SystemExit(f"Failed to load SportRadar data: {exc}") from exc

connection = get_connection()
cursor = connection.cursor()

# Insert categories
category_query = """
    INSERT INTO categories (category_id, category_name)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE
        category_name = VALUES(category_name)
"""

for category in categories:
    cursor.execute(
        category_query,
        (
            category["category_id"],
            category["category_name"]
        )
    )


# Insert competitions
competition_query = """
    INSERT INTO competitions
    (
        competition_id,
        competition_name,
        parent_id,
        type,
        gender,
        level,
        category_id
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        competition_name = VALUES(competition_name),
        parent_id = VALUES(parent_id),
        type = VALUES(type),
        gender = VALUES(gender),
        level = VALUES(level),
        category_id = VALUES(category_id)
"""

for competition in competitions:
    cursor.execute(
        competition_query,
        (
            competition["competition_id"],
            competition["competition_name"],
            competition["parent_id"],
            competition["type"],
            competition["gender"],
            competition["level"],
            competition["category_id"]
        )
    )


connection.commit()

print("Categories inserted:", len(categories))
print("Competitions inserted:", len(competitions))

cursor.close()
connection.close()