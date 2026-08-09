import os
from dotenv import load_dotenv
import requests
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()

API_KEY = os.getenv("SPORTRADAR_API_KEY")
if not API_KEY:
    raise RuntimeError("SPORTRADAR_API_KEY is not set in the environment.")

URL = "https://api.sportradar.com/tennis/trial/v3/en/complexes.json"
HEADERS = {"x-api-key": API_KEY}


def _get_session(retries=3, backoff_factor=0.5, status_forcelist=(502, 503, 504)):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=("GET", "POST"),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def fetch_complexes_raw(timeout=20):
    session = _get_session()
    try:
        resp = session.get(URL, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise RuntimeError("Unable to fetch complexes data. Check network, API key, and endpoint.") from exc
    return resp


def fetch_complexes_data(timeout=20):
    resp = fetch_complexes_raw(timeout=timeout)
    data = resp.json()
    return parse_complexes_data(data)


def parse_complexes_data(data):
    complexes = []
    venues = []

    for complex_item in data.get("complexes", []):
        complexes.append({
            "complex_id": complex_item.get("id"),
            "complex_name": complex_item.get("name")
        })

        for venue in complex_item.get("venues", []):
            # Support both nested objects and flat keys like 'city_name' returned by the API
            city_name = (venue.get("city") or {}).get("name") if isinstance(venue.get("city"), dict) else venue.get("city_name")
            country = venue.get("country") or {}
            country_name = country.get("name") if isinstance(country, dict) else venue.get("country_name")
            country_code = country.get("code") if isinstance(country, dict) else venue.get("country_code")

            venues.append({
                "venue_id": venue.get("id"),
                "venue_name": venue.get("name"),
                "city_name": city_name,
                "country_name": country_name,
                "country_code": country_code,
                "timezone": venue.get("timezone"),
                "complex_id": complex_item.get("id")
            })

    return complexes, venues


if __name__ == "__main__":
    # Print Status and full JSON response for debugging/inspection
    try:
        resp = fetch_complexes_raw()
    except RuntimeError as e:
        print("Error:", e)
        raise SystemExit(1)
    print("Status:", resp.status_code)
    try:
        parsed = resp.json()
    except ValueError:
        print("Response is not JSON")
        raise SystemExit(1)

    # Use the parser to extract structured lists
    complexes_list, venues_list = parse_complexes_data(parsed)

    # Print a concise summary
    print(f"Complexes: {len(complexes_list)}")
    print(f"Venues: {len(venues_list)}")

    # Show samples (first item) for quick inspection
    if complexes_list:
        print("Sample complex:")
        print(json.dumps(complexes_list[0], indent=2))
    if venues_list:
        print("Sample venue:")
        print(json.dumps(venues_list[0], indent=2))

    # Optionally print full JSON when debugging large outputs
    if os.getenv("PRINT_FULL_JSON", "false").lower() in ("1", "true", "yes"):
        print("Full JSON:")
        print(json.dumps(parsed, indent=2))
