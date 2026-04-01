import pandas as pd
from typing import Type
from pydantic import BaseModel
from langchain.tools import BaseTool
from pathlib import Path
from app.models.loader import predict_crop
from app.core.user_context import get_active_location, get_active_state, get_current_user, set_user_crop
from app.services.weather_service import get_weather_data
from app.services.npk_ph_level import get_soil_data_for_state
import json


class EmptyInput(BaseModel):
    pass


class CropRecommendationInternalTool(BaseTool):
    name: str = "crop_recommendation_internal"
    description: str = (
        "Recommends the best crop to plant based on real-time weather and soil data for the farmer's GPS location. "
        "Does NOT require user input. "
        "Use this for real-time soil and climate-based crop suggestions."
    )
    args_schema: Type[BaseModel] = EmptyInput
    def _run(self) -> str:
        try:
            # -----------------------------
            # 1. LOCATION
            # -----------------------------
            lat, lon = get_active_location()

            if lat is None or lon is None:
                # fallback to Dehradun
                lat, lon = 30.3165, 78.0322


            # -----------------------------
            # 2. MODEL PATH
            # -----------------------------
            model_path = Path(__file__).resolve().parent.parent / "models" / "crop_prediction_model.pkl"

            if not model_path.exists():
                return "❌ Model file not found"

            # -----------------------------
            # 3. WEATHER (FORECAST FORMAT FIXED)
            # -----------------------------
            weather = get_weather_data(lat, lon)

            # if API returns string → convert
            if isinstance(weather, str):
                weather = json.loads(weather)

            forecast = weather.get("forecast", [])
            if not forecast:
                return "❌ No forecast data available"

            today = forecast[0]
            snapshots = today.get("snapshots", {})

            # prefer afternoon (best for agriculture estimation)
            afternoon = snapshots.get("Afternoon") or snapshots.get("Morning") or {}

            temp = afternoon.get("temp_C", 25.0)
            rain = today.get("chance_of_rain_pct", 0)

            # humidity not available in your API → fallback
            hum = 60.0

            # -----------------------------
            # 4. SOIL DATA
            # -----------------------------
            state = get_active_state()
            soil_data = get_soil_data_for_state(state) if state else {}

            n = soil_data.get("N", 90)
            p = soil_data.get("P", 42)
            k = soil_data.get("K", 43)
            ph = soil_data.get("pH") or 6.5

            # -----------------------------
            # 5. PREDICTION
            # -----------------------------
            prediction, confidence = predict_crop(
                str(model_path),
                n, p, k,
                temp, hum, ph, rain
            )

            # -----------------------------
            # 6. SAVE TO USER PROFILE
            # -----------------------------
            user = get_current_user()
            if user:
                try:
                    set_user_crop(user, prediction)
                except Exception as db_err:
                    print(f"[DB] Warning: {db_err}")

            # -----------------------------
            # 7. RESPONSE
            # -----------------------------
            return (
                "🌱 Crop Recommendation Analysis\n"
                "----------------------------------\n"
                f"📍 Location: ({lat:.4f}, {lon:.4f})\n"
                f"🌡️ Temperature: {temp}°C\n"
                f"💧 Rain Chance: {rain}%\n"
                f"🌱 Soil: N:{n} P:{p} K:{k} | pH:{ph}\n\n"
                f"🌾 Suggested Crop: {prediction.upper()}\n"
            )

        except Exception as e:
            return f"❌ Error during crop recommendation: {str(e)}"

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not implemented")