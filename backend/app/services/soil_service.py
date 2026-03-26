
    
    
import os
import requests
from requests_cache import CachedSession
from datetime import timedelta

# 1. Initialize a specific Soil Session
# This replaces the global install_cache()
soil_session = CachedSession(
    cache_name=os.path.join("app", "data", "soil_cache"),
    backend='sqlite',
    expire_after=timedelta(minutes=10), # Case 1: 10-minute speed booster
    stale_if_error=True,                # Case 2: API-down safety net
    allowable_codes=[200],              # Only cache successful soil data
    ignored_parameters=['polyid','appid']
)



def fetch_soil_data() -> dict:
    """
    Fetch soil data for the farmer's polygon from AgroMonitoring API with requests_cache.
    """
    polyid = os.getenv("AGRO_POLYGON_ID")
    appid = os.getenv("AGRO_MONOTRONIG_API")

    if not polyid or not appid:
        raise ValueError("Polygon ID or API key not set in environment variables.")

    url = f"http://api.agromonitoring.com/agro/1.0/soil?polyid={polyid}&appid={appid}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    # --- Debugging Logic ---
        if response.from_cache:
            if getattr(response, 'is_expired', False):
                print("⚠️ API DOWN: Serving stale soil data from backup.")
            else:
                print("🚀 CACHE HIT: Serving fresh data (under 10 mins old).")
        else:
            print("🌐 API CALL: Fetched new soil data from AgroMonitoring.")
            
        return response.json()

    except requests.RequestException as e:
        # This only triggers if the API is down AND there is NO cache at all
        raise RuntimeError(f"Critical Error: Soil data unreachable: {str(e)}")

if __name__ == "__main__":
    print(fetch_soil_data())