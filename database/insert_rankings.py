import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from api.rankings_api import fetch_rankings_raw, parse_rankings_data
from database.connection import get_connection


try:
    response = fetch_rankings_raw()
    data = response.json()
    competitors, rankings = parse_rankings_data(data)
except RuntimeError as exc:
    raise SystemExit(f"Failed to load rankings data: {exc}") from exc
except ValueError as exc:
    raise SystemExit("Response is not valid JSON") from exc

connection = get_connection()
cursor = connection.cursor()


# Insert competitors
competitor_query = """
INSERT INTO competitors (
    competitor_id,
    name,
    country,
    country_code,
    abbreviation
)
VALUES (%s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    country = VALUES(country),
    country_code = VALUES(country_code),
    abbreviation = VALUES(abbreviation)
"""

for competitor in competitors:
    cursor.execute(
        competitor_query,
        (
            competitor["competitor_id"],
            competitor["name"],
            competitor["country"] or "",
            competitor["country_code"] or "",
            competitor["abbreviation"] or ""
        )
    )


# Insert rankings
ranking_query = """
INSERT INTO competitor_rankings (
    `rank`,
    movement,
    points,
    competitions_played,
    competitor_id
)
VALUES (%s, %s, %s, %s, %s)
"""

for ranking in rankings:
    cursor.execute(
        ranking_query,
        (
            ranking["rank"],
            ranking["movement"] or 0,
            ranking["points"] or 0,
            ranking["competitions_played"] or 0,
            ranking["competitor_id"]
        )
    )


connection.commit()

print("Competitors inserted:", len(competitors))
print("Rankings inserted:", len(rankings))


cursor.close()
connection.close()