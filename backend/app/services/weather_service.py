import os
import requests
from requests_cache import CachedSession
from datetime import timedelta
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY") 
LAT = 33.44
LON = -94.04
UNITS = "metric"

# Initialize cache (10-minute expiry)
weather_session = CachedSession(
    'app/data/weather_cache',       # Path to your sqlite file
    backend='sqlite',
    expire_after=timedelta(minutes=10), 
    stale_if_error=True,            # USE OLD DATA ONLY IF API IS DOWN
    allowable_codes=[200],          # Don't cache 401/404/500 errors
    ignored_parameters=['appid']
)

def get_weather_data(lat, lon):
    if not API_KEY:
        return {"error": "API Key missing in .env"}
    
    # Keep the base URL clean
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": UNITS
    }

    try:
        # ✅ USE THE SESSION, NOT THE REQUESTS MODULE
        response = weather_session.get(base_url, params=params)
        response.raise_for_status()

        # Check if the response came from the cache
        # Note: requests-cache adds 'from_cache' to the response object
        is_from_cache = getattr(response, 'from_cache', False)
        
        if is_from_cache:
            # Check if it was a 'stale' fallback (Case 2)
            if getattr(response, 'is_expired', False):
                print("⚠️ Case 2: API is down! Serving 'stale' fallback data.")
            else:
                print("🚀 Case 1: Serving from cache (Fresh).")
        else:
            print("🌐 Case 3: 10 mins passed or cache empty. Fetched fresh data.")

        return response.json()

    except Exception as e:
        return {"error": f"Critical Failure (No cache and no API): {e}"}

if __name__ == "__main__":
    # --- CHANGE EXCLUSIONS HERE ---
    # Options: "current", "minutely", "hourly", "daily", "alerts"
    data = get_weather_data(LAT, LON)
    print(data)
        
"""
Value:What it removes from the response
current: "Current weather conditions (temp, humidity, etc.)."
minutely: Minute-by-minute precipitation forecast for the next 1 hour.
hourly: Hourly forecast for the next 48 hours.
daily: Daily forecast for the next 8 days.
alerts: Government-issued weather warnings/alerts.
"""
