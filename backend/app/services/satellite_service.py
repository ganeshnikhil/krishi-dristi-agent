
### FOR TEMPRATURE 
import requests
import json
import pandas as pd
import re
import os

# Configuration
BASE_URL = "https://imdgeospatial.imd.gov.in/Min_Temperature/data/"
OUTPUT_DIR = "imd_data_snapshot"

# Files from your HTML source
DATA_FILES = {
    "stations": "StationData_11.js",
    "heatwave": "HeatWaveStatus_12.js",
    "warmnight": "WarmNightStatus_13.js"
}

# Image Metadata (Bounds)
IMAGE_METADATA = {
    "RelativeHumidityMapPrevDay_0.png": [6.753248857767442, 68.1835865617193, 37.08230146339119, 97.4224285894075],
    "MaxDeparturefrom90Pct_1.png": [6.755952899606655, 68.18624899229724, 37.07826805962333, 97.41529266802229],
    "MaxDeparturefrom95Pct_2.png": [6.755952899606655, 68.18624899229724, 37.07826805962333, 97.41529266802229],
    "MaxDeparturefrom98Pct_3.png": [6.755952899606655, 68.18624899229724, 37.07826805962333, 97.41529266802229],
    "MaxDepartureMapfromNorm_4.png": [6.753248857767442, 68.1835865617193, 37.08230146339119, 97.4224285894075],
    "MinDepartureMap_5.png": [6.755952899606655, 68.18624899229724, 37.07826805962333, 97.41529266802229],
    "MaxTemperatureMapPrevDay_6.png": [6.753248857767442, 68.1835865617193, 37.08230146339119, 97.4224285894075],
    "MinTemperatureMap_7.png": [6.753248857767442, 68.1835865617193, 37.08230146339119, 97.4224285894075]
}

def setup_folders():
    os.makedirs(f"{OUTPUT_DIR}/maps", exist_ok=True)

def fetch_js_as_json(filename):
    try:
        r = requests.get(BASE_URL + filename, timeout=15)
        r.raise_for_status()
        # Clean the JS variable wrapper
        clean_json = re.sub(r'^var\s+\w+\s*=\s*', '', r.text.strip()).rstrip(';')
        return json.loads(clean_json)
    except Exception as e:
        print(f"Error fetching {filename}: {e}")
        return None

def process_table_data():
    print("--- 📊 Processing Station Tables ---")
    raw_json = fetch_js_as_json(DATA_FILES["stations"])
    if not raw_json: return

    rows = []
    for feature in raw_json.get("features", []):
        p = feature.get("properties", {})
        
        # --- FIX: Null-Safe Geometry Check ---
        geom = feature.get("geometry")
        coords = geom.get("coordinates", [None, None]) if geom else [None, None]
        
        rows.append({
            "Date": p.get("Date"),
            "Station": p.get("Station_Name"),
            "Code": p.get("Station_Code"),
            "Max_Temp_C": p.get("Previous_Day_Max_temp"),
            "Max_Depart": p.get("Previous_Day_Max_Departure_from_Normal"),
            "Min_Temp_C": p.get("Today_Min_temp"),
            "Min_Depart": p.get("Today_Min_Departure_from_Normal"),
            "Humidity_%": p.get("Previous_Day_Relative_Humidity_at_1730"),
            "Lat": coords[1],
            "Lon": coords[0]
        })
    
    df = pd.DataFrame(rows)
    csv_path = f"{OUTPUT_DIR}/imd_weather_stations.csv"
    df.to_csv(csv_path, index=False)
    print(f"✅ Table saved: {csv_path} ({len(df)} rows)")

def download_images():
    print("\n--- 🗺️ Downloading Heatmap Images ---")
    for img_name, bounds in IMAGE_METADATA.items():
        try:
            img_url = BASE_URL + img_name
            r = requests.get(img_url, stream=True, timeout=20)
            r.raise_for_status()
            
            save_path = f"{OUTPUT_DIR}/maps/{img_name}"
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Save bounds metadata
            with open(save_path.replace(".png", ".txt"), "w") as meta:
                meta.write(f"Bounds: {bounds}")
            
            print(f"✅ Downloaded: {img_name}")
        except Exception as e:
            print(f"❌ Failed {img_name}: {e}")

if __name__ == "__main__":
    setup_folders()
    process_table_data()
    # download_images()
    # print("\n🚀 Tasks complete.")
    
    
    