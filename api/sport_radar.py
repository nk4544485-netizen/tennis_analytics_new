import os
from dotenv import load_dotenv
import requests

load_dotenv()

API_KEY = os.getenv("SPORTRADAR_API_KEY")
if not API_KEY:
    raise RuntimeError("SPORTRADAR_API_KEY is not set in the environment.")

URL = "https://api.sportradar.com/tennis/trial/v3/en/competitions.json"
HEADERS = {
    "accept": "application/json",
    "x-api-key": API_KEY
}


def fetch_sport_radar_data():
    try:
        response = requests.get(URL, headers=HEADERS, timeout=20)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(
            "Unable to fetch SportRadar data. " \
            "Check your network, API key, and endpoint." \
            f" Original error: {exc}"
        ) from exc

    data = response.json()
    return parse_sport_radar_data(data)


def parse_sport_radar_data(data):
    categories = []
    competitions = []

    for competition in data.get("competitions", []):
        category = competition["category"]

        categories.append({
            "category_id": category["id"],
            "category_name": category["name"]
        })

        competitions.append({
            "competition_id": competition["id"],
            "competition_name": competition["name"],
            "parent_id": competition.get("parent_id"),
            "type": competition["type"],
            "gender": competition["gender"],
            "level": competition.get("level"),
            "category_id": category["id"]
        })

    return categories, competitions


if __name__ == "__main__":
    categories, competitions = fetch_sport_radar_data()
    print(categories[:3])
    print(competitions[:3])
