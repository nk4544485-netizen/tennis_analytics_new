import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from api.complexes_api import fetch_complexes_data
from database.connection import get_connection


try:
    complexes, venues = fetch_complexes_data()
except RuntimeError as exc:
    raise SystemExit(f"Failed to load complexes data: {exc}") from exc

connection = get_connection()
cursor = connection.cursor()


def safe_text(value):
    return value if value is not None else ""

# Insert complexes
complex_query = """
INSERT INTO complexes (complex_id, complex_name)
VALUES (%s, %s)
ON DUPLICATE KEY UPDATE
    complex_name = VALUES(complex_name)
"""

for complex_data in complexes:
    cursor.execute(
        complex_query,
        (
            complex_data["complex_id"],
            complex_data["complex_name"]
        )
    )


# Insert venues
venue_query = """
INSERT INTO venues (
    venue_id,
    venue_name,
    city_name,
    country_name,
    country_code,
    timezone,
    complex_id
)
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    venue_name = VALUES(venue_name),
    city_name = VALUES(city_name),
    country_name = VALUES(country_name),
    country_code = VALUES(country_code),
    timezone = VALUES(timezone),
    complex_id = VALUES(complex_id)
"""

for venue in venues:
    cursor.execute(
        venue_query,
        (
            venue["venue_id"],
            venue["venue_name"],
            safe_text(venue.get("city_name")),
            safe_text(venue.get("country_name")),
            safe_text(venue.get("country_code")),
            safe_text(venue.get("timezone")),
            venue["complex_id"]
        )
    )


connection.commit()

print("Complexes inserted:", len(complexes))
print("Venues inserted:", len(venues))

cursor.close()
connection.close()