import os
import requests
import requests_cache
from datetime import timedelta
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY") 
LAT = 33.44
LON = -94.04
UNITS = "metric"

# Initialize cache (10-minute expiry)
requests_cache.install_cache(
    'app/data/weather_cache.sqlite', 
    backend='sqlite', 
    expire_after=timedelta(minutes=10)
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
        
        is_from_cache = getattr(response, 'from_cache', False)
        print(f"--- Data source: {'[CACHE]' if is_from_cache else '[API CALL]'} ---")
        
        return response.json()
        
    except requests.exceptions.HTTPError as err:
        return {"error": f"HTTP Error: {err}"}

if __name__ == "__main__":
    # --- CHANGE EXCLUSIONS HERE ---
    # Options: "current", "minutely", "hourly", "daily", "alerts"
    to_exclude = ["minutely"] 
    
    data = get_weather_data(LAT, LON, exclude_list=to_exclude)
    if "error" not in data:
        # If 'current' was NOT excluded, we can print it
        if 'current' in data:
            print(f"Current Temp: {data['current']['temp']}°C")
        
        # If 'alerts' was NOT excluded, we can print them
        if 'alerts' in data:
            print(f"Alerts found: {len(data['alerts'])}")
        else:
            print("No alerts in response (either excluded or none active).")
            
        # Proof of exclusion:
        excluded_keys = [k for k in to_exclude if k not in data]
        print(f"Successfully excluded: {', '.join(excluded_keys)}")
    else:
        print(f"Error: {data['error']}")
        
"""
Value:What it removes from the response
current: "Current weather conditions (temp, humidity, etc.)."
minutely: Minute-by-minute precipitation forecast for the next 1 hour.
hourly: Hourly forecast for the next 48 hours.
daily: Daily forecast for the next 8 days.
alerts: Government-issued weather warnings/alerts.
"""
