import os
from dotenv import load_dotenv
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()

API_KEY = os.getenv("SPORTRADAR_API_KEY")
if not API_KEY:
    raise RuntimeError("SPORTRADAR_API_KEY is not set in the environment.")

URL = "https://api.sportradar.com/tennis/trial/v3/en/double_competitors_race_rankings.json"

HEADERS = {
    "x-api-key": API_KEY
}


def _get_session(retries=3, backoff_factor=0.5):
    session = requests.Session()

    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=(502, 503, 504),
        allowed_methods=("GET",)
    )

    adapter = HTTPAdapter(max_retries=retry)

    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session


def fetch_rankings_raw(timeout=20):
    session = _get_session()

    try:
        response = session.get(
            URL,
            headers=HEADERS,
            timeout=timeout
        )

        response.raise_for_status()

    except requests.exceptions.RequestException as exc:
        raise RuntimeError(
            "Unable to fetch rankings data. "
            "Check network, API key, and endpoint."
        ) from exc

    return response


def parse_rankings_data(data):

    competitors = []
    rankings = []

    for ranking_group in data.get("rankings", []):

        for item in ranking_group.get("competitor_rankings", []):

            competitor = item.get("competitor", {})

            competitor_id = competitor.get("id")

            if not competitor_id:
                continue

            competitors.append({
                "competitor_id": competitor_id,
                "name": competitor.get("name"),
                "country": competitor.get("country"),
                "country_code": competitor.get("country_code"),
                "abbreviation": competitor.get("abbreviation")
            })

            rankings.append({
                "rank": item.get("rank"),
                "movement": item.get("movement"),
                "points": item.get("points"),
                "competitions_played": item.get("competitions_played"),
                "competitor_id": competitor_id
            })

    return competitors, rankings


if __name__ == "__main__":

    try:
        response = fetch_rankings_raw()

        print("Status:", response.status_code)

        data = response.json()

        competitors, rankings = parse_rankings_data(data)

        print("Competitors:", len(competitors))
        print("Rankings:", len(rankings))

        print("\nFirst 3 Competitors:")
        print(json.dumps(competitors[:3], indent=2))

        print("\nFirst 3 Rankings:")
        print(json.dumps(rankings[:3], indent=2))

    except RuntimeError as exc:
        print("Error:", exc)

    except ValueError:
        print("Response is not valid JSON.")