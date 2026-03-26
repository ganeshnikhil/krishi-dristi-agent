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



def get_weather_data(lat, lon,):
    """
    Fetches weather data. 
    exclude_list: list of strings (e.g., ["minutely", "hourly"])
    """
    if not API_KEY:
        return {"error": "API Key missing in .env"}

    base_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}"
    
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
    }
    

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        # Case 1: Multiple requests in 10 mins
        if response.from_cache and not getattr(response, 'is_expired', False):
            print("🚀 Case 1 Triggered: Serving from cache (Under 10 mins old).")
            
        # Case 2: API is down (and data is > 10 mins old)
        elif response.from_cache and getattr(response, 'is_expired', False):
            print("⚠️ Case 2 Triggered: API is down! Serving 'stale' fallback data.")
            
        # Case 3: Fresh API call (Data was old AND API is working)
        else:
            print("🌐 10 mins passed & API is healthy: Fetched fresh data.")

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
