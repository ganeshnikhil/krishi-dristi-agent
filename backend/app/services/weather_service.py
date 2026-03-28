import os
import requests
from requests_cache import CachedSession
from datetime import timedelta
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()


API_KEY = os.getenv("WEATHER_API_FORECAST") 
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




import requests
import json

def get_weather_data(lat, lon, days=3):
    url = "http://api.weatherapi.com/v1/forecast.json"
    
    params = {
        "key": API_KEY,
        "q": f"{lat},{lon}",
        "days": days,
        "aqi": "no",     # LLMs rarely need Air Quality unless explicitly requested
        "alerts": "no"   # Keeps the payload lean
    }
    
    res = requests.get(url, params=params)
    
    if res.status_code != 200:
        return f"Error fetching weather: {res.text}"
    
    raw_data = res.json()
    
    # Build a highly readable, token-efficient dictionary
    llm_context = {
        "location": raw_data["location"]["name"],
        "forecast": []
    }
    
    for day in raw_data["forecast"]["forecastday"]:
        day_data = day["day"]
        
        # 1. Extract the daily overview
        daily_summary = {
            "date": day["date"],
            "condition": day_data["condition"]["text"],
            "high_C": day_data["maxtemp_c"],
            "low_C": day_data["mintemp_c"],
            "chance_of_rain_pct": day_data["daily_chance_of_rain"],
            "snapshots": {}
        }
        
        # 2. Sample the hourly data (Morning, Afternoon, Evening)
        # LLMs don't need all 24 hours to understand the day's progression
        target_hours = {8: "Morning", 14: "Afternoon", 20: "Evening"}
        
        for hour in day["hour"]:
            # Extract the hour integer (e.g., from "2026-03-29 14:00")
            hour_int = int(hour["time"].split(" ")[1].split(":")[0])
            
            if hour_int in target_hours:
                time_label = target_hours[hour_int]
                daily_summary["snapshots"][time_label] = {
                    "temp_C": hour["temp_c"],
                    "condition": hour["condition"]["text"]
                }
                
        llm_context["forecast"].append(daily_summary)
        
    # Return as a compact string, ready to be injected into an f-string prompt
    return json.dumps(llm_context, indent=2)



# def get_weather_data(lat, lon):
#     if not API_KEY:
#         return {"error": "API Key missing in .env"}
    
#     # Keep the base URL clean
#     base_url = "https://api.openweathermap.org/data/2.5/weather"
    
#     params = {
#         "lat": lat,
#         "lon": lon,
#         "appid": API_KEY,
#         "units": UNITS
#     }

#     try:
#         # ✅ USE THE SESSION, NOT THE REQUESTS MODULE
#         response = weather_session.get(base_url, params=params)
#         response.raise_for_status()

#         # Check if the response came from the cache
#         # Note: requests-cache adds 'from_cache' to the response object
#         is_from_cache = getattr(response, 'from_cache', False)
        
#         if is_from_cache:
#             # Check if it was a 'stale' fallback (Case 2)
#             if getattr(response, 'is_expired', False):
#                 print("⚠️ Case 2: API is down! Serving 'stale' fallback data.")
#             else:
#                 print("🚀 Case 1: Serving from cache (Fresh).")
#         else:
#             print("🌐 Case 3: 10 mins passed or cache empty. Fetched fresh data.")

#         return response.json()

#     except Exception as e:
#         return {"error": f"Critical Failure (No cache and no API): {e}"}

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
