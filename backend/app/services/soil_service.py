
    
    
import os
import requests
import requests_cache
from datetime import timedelta

# ✅ Initialize cache in app/data folder
cache_path = os.path.join("app", "data", "weather_cache")  # SQLite file will be weather_cache.sqlite
requests_cache.install_cache(
    cache_name=cache_path,
    backend='sqlite',
    expire_after=timedelta(minutes=10)  # cache expires after 10 minutes
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
        return response.json()
    except requests.RequestException as e:
        raise RuntimeError(f"Unable to fetch soil data: {str(e)}")