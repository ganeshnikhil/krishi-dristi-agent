import os
import requests
from datetime import timedelta
from dotenv import load_dotenv
from requests_cache import CachedSession

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

AMBEE_API_KEY = os.getenv("AMBEE_DISASTER_API")

if not AMBEE_API_KEY:
    raise ValueError("AMBEE_API_KEY not found in .env file")


# -----------------------------
# Cached Session (Soil/Disaster API)
# -----------------------------
soil_session = CachedSession(
    cache_name=os.path.join("app", "data", "soil_cache"),
    backend="sqlite",
    expire_after=timedelta(minutes=10),  # cache duration
    stale_if_error=True,                 # fallback if API fails
    allowable_codes=[200],               # cache only successful responses
)

def parse_disaster_data(data):
    """
    Extract date, event_name, proximity_severity_level, default_alert_levels
    from all events in result list.
    """

    results = data.get("result", [])

    output = []

    for event in results:
        output.append({
            "date": event.get("date"),
            "event_name": event.get("event_name"),
            "proximity_severity_level": event.get("proximity_severity_level"),
            "default_alert_levels": event.get("default_alert_levels")
        })

    return output



# -----------------------------
# Disaster API Function
# -----------------------------
def get_latest_disaster(lat: float, lng: float):
    """
    Fetch latest disaster data from Ambee API with caching.
    """

    url = "https://api.ambeedata.com/disasters/latest/by-lat-lng"

    headers = {
        "x-api-key": AMBEE_API_KEY,
        "Content-type": "application/json"
    }

    params = {
        "lat": lat,
        "lng": lng
    }

    try:
        response = soil_session.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return parse_disaster_data(data)
    

    except requests.exceptions.RequestException as e:
        return {
            "error": True,
            "message": str(e)
        }


# -----------------------------
# Example Usage
# -----------------------------
if __name__ == "__main__":
    data = get_latest_disaster(-15.76166996, -72.48771045489497)
    print(data)
"""
{'date': '2026-03-22 15:00:00', 'event_name': 'Earthquake in Peru', 'proximity_severity_level': 'Moderate Risk', 'default_alert_levels': 'Red'}, {'date': '2026-03-12 04:00:00', 'event_name': 'Earthquake in Peru', 'proximity_severity_level': 'Moderate Risk', 'default_alert_levels': 'Red'}]


"""
