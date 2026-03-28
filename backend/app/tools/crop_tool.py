import pandas as pd
from typing import Type
from pydantic import BaseModel
from langchain.tools import BaseTool
from pathlib import Path
from app.models.loader import predict_crop
from app.core.user_context import get_active_location, get_current_user, set_user_crop
from app.services.weather_service import get_weather_data

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
        lat, lon = get_active_location()
        model_path = str(Path(__file__).resolve().parent.parent / "models" / "crop_prediction_model.pkl")

        try:
            # Fetch real weather for the user's location
            weather = get_weather_data(lat, lon)
            temp = weather.get("main", {}).get("temp", 25.0)
            hum  = weather.get("main", {}).get("humidity", 60.0)
            rain = weather.get("rain", {}).get("1h", weather.get("rain", {}).get("3h", 50.0))

            # Soil NPK and pH — these come from your crop prediction model defaults
            # They are good average values; can later be replaced with a soil API
            n, p, k = 90, 42, 43
            ph = 6.5

            prediction, confidence = predict_crop(
                model_path, n, p, k,
                temp, hum, ph, rain
            )

            # ✅ Persist the predicted crop for this user so other tools
            # (like fertilizer) can use it without asking again
            user = get_current_user()
            if user:
                try:
                    set_user_crop(user, prediction)
                    print(f"[DB] ✅ Saved crop '{prediction}' for user '{user}'")
                except Exception as db_err:
                    print(f"[DB] ⚠️ Failed to save crop for user '{user}': {db_err}")
            else:
                print("[DB] ⚠️ No active user found — crop not saved to DB")

            return (
                "🌱 **Crop Recommendation Analysis**:\n"
                "----------------------------------\n"
                f"📍 **Location**: ({lat:.4f}, {lon:.4f})\n"
                f"📍 **Soil Stats**: N:{n}, P:{p}, K:{k} | pH: {ph}\n"
                f"🌦️ **Climate**: {temp}°C | {hum}% Humidity | {rain}mm Rain\n\n"
                f"✅ **Suggested Crop**: {prediction.upper()}\n"
                f"📊 **Model Confidence**: {confidence * 100:.2f}%"
            )

        except Exception as e:
            return f"❌ Error during crop recommendation: {str(e)}"

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not implemented")
