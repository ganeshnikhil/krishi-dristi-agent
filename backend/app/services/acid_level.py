import requests
import csv
import time

def get_soil_attributes(lat, lon):
    """
    Queries the Bhoomi Geoserver for soil properties at a specific Lat/Lon.
    """
    base_url = "https://bhoomigeoportal-nbsslup.in/geoserver/wms"
    
    # Define a tiny bounding box (approx 10m x 10m) around the point
    delta = 0.0001 
    bbox = f"{lat-delta},{lon-delta},{lat+delta},{lon+delta}"
    
    params = {
        "SERVICE": "WMS",
        "VERSION": "1.3.0",
        "REQUEST": "GetFeatureInfo",
        "LAYERS": "nbss_geoserver:Acid_Soils_Of_India", # Change this for other layers
        "QUERY_LAYERS": "nbss_geoserver:Acid_Soils_Of_India",
        "INFO_FORMAT": "application/json",
        "I": "50",
        "J": "50",
        "WIDTH": "101",
        "HEIGHT": "101",
        "CRS": "EPSG:4326",
        "BBOX": bbox
    }

    try:
        response = requests.get(base_url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['features']:
                # Returns the dictionary of properties (pH, Soil Type, etc.)
                return data['features'][0]['properties']['STATE']
            else:
                return {"error": "No data at this location"}
    except Exception as e:
        return {"error": str(e)}
    
    return {"error": "Server unavailable"}

lat , lon = 10.52, 76.21
print(get_soil_attributes(lat , lon))