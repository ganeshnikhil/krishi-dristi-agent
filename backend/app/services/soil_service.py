import os
import requests
from requests_cache import CachedSession
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

# 1. Initialize a specific Soil Session
# This replaces the global install_cache()
soil_session = CachedSession(
    cache_name=os.path.join("app", "data", "soil_cache"),
    backend='sqlite',
    expire_after=timedelta(minutes=10), # Case 1: 10-minute speed booster
    stale_if_error=True,                # Case 2: API-down safety net
    allowable_codes=[200],              # Only cache successful soil data
)

def fetch_soil_data() -> dict:
    """
    Fetch soil data for the farmer's polygon from AgroMonitoring API with requests_cache.
    """
    polyid = os.getenv("AGRO_POLYGON_ID")
    appid = os.getenv("AGRO_MONOTRONIG_API")
    if not polyid or not appid:
        raise ValueError("Polygon ID or API key not set in environment variables.")

    # Clean URL without query strings
    url = "http://api.agromonitoring.com/agro/1.0/soil"
    

    # Let the session handle the encoding of parameters
    params = {
        "polyid": polyid,
        "appid": appid
    }

    try:
        # ✅ CHANGE: Use soil_session instead of requests
        response = soil_session.get(url, params=params, timeout=10)
        response.raise_for_status()

        # Now .from_cache will actually exist!
        is_cached = getattr(response, 'from_cache', False)

        if is_cached:
            if getattr(response, 'is_expired', False):
                print("⚠️ API DOWN: Serving stale soil data from backup.")
            else:
                print("🚀 CACHE HIT: Serving fresh data (under 10 mins old).")
        else:
            print("🌐 API CALL: Fetched new soil data from AgroMonitoring.")
            
        return response.json()

    except Exception as e:
        # This triggers if the API is down AND there is NO cache at all
        raise RuntimeError(f"Critical Error: Soil data unreachable: {str(e)}")


# import requests

# # Use your API Key
# API_KEY = "43c4552bed6354941cde6768d5890f47"
# url = f"http://api.agromonitoring.com/agro/1.0/polygons?appid={API_KEY}"

# response = requests.get(url)
# polygons = response.json()

# print("--- Your Registered Polygons ---")
# for poly in polygons:
#     print(f"Name: {poly['name']}")
#     print(f"ID:   {poly['id']}")  # <--- THIS IS THE VALUE YOU NEED
#     print("-" * 30)
    
if __name__ == "__main__":
    print(fetch_soil_data())