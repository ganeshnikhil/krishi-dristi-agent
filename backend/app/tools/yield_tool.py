from typing import Type, Optional
from pydantic import BaseModel, Field
from pathlib import Path
from langchain.tools import BaseTool
from app.models.loader import predict_yield_simple, predict_crop
from app.services.weather_service import get_weather_data
from app.core.user_context import (
    get_active_location, get_active_state, get_active_crop,
    get_current_user, set_user_crop
)
from app.services.npk_ph_level import get_soil_data_for_state


class YieldInput(BaseModel):
    crop_name: Optional[str] = Field(
        default=None,
        description="The crop name (e.g., 'Rice', 'Wheat'). Leave empty to auto-detect from DB or prediction."
    )


class YieldPredictionInternalTool(BaseTool):
    name: str = "yield_prediction_internal"
    description: str = (
        "Predicts the crop yield for the farmer's GPS location using real-time weather data. "
        "Automatically reads the farmer's last predicted crop from the database. "
        "If no crop is in the database yet, it runs the crop prediction automatically. "
        "Only pass 'crop_name' if the user explicitly mentions a specific crop."
    )
    args_schema: Type[BaseModel] = YieldInput

    def _run(self, crop_name: Optional[str] = None) -> str:
        lat, lon = get_active_location()

        # fallback to Dehradun if invalid
        if lat is None or lon is None:
            lat, lon = 30.3165, 78.0322
        
        yield_model = str(Path(__file__).resolve().parent.parent / "models" / "india_crop_yield_model.pkl")
        crop_model  = str(Path(__file__).resolve().parent.parent / "models" / "crop_prediction_model.pkl")

        # ── Resolve crop ──────────────────────────────────────────────────────
        # Priority: 1) user passed crop_name in message
        #           2) last predicted crop saved in DB
        #           3) auto-run crop prediction and save result
        auto_predicted = False
        resolved_crop  = crop_name or get_active_crop()

        if not resolved_crop:
            try:
                weather = get_weather_data(lat, lon)
                temp = weather.get("main", {}).get("temp", 25.0)
                hum  = weather.get("main", {}).get("humidity", 60.0)
                rain = weather.get("rain", {}).get("1h", weather.get("rain", {}).get("3h", 50.0))
                
                state = get_active_state()
                soil_data = get_soil_data_for_state(state) if state else None
                if soil_data:
                    n, p, k = soil_data["N"], soil_data["P"], soil_data["K"]
                    ph = soil_data["pH"] if soil_data["pH"] is not None else 6.5
                else:
                    n, p, k, ph = 90, 42, 43, 6.5

                predicted, _ = predict_crop(crop_model, n, p, k, temp, hum, ph, rain)
                resolved_crop = predicted
                auto_predicted = True

                user = get_current_user()
                if user:
                    try:
                        set_user_crop(user, resolved_crop)
                        print(f"[DB] ✅ Auto-saved crop '{resolved_crop}' for user '{user}'")
                    except Exception as db_err:
                        print(f"[DB] ⚠️ Could not save crop: {db_err}")

            except Exception as crop_err:
                return (
                    f"❌ Could not auto-predict crop: {crop_err}\n"
                    "Please ask 'what crop should I grow?' first, or say e.g. 'predict yield for wheat'."
                )

        try:
            weather = get_weather_data(lat, lon)
            current_temp = weather.get("main", {}).get("temp", 28.4)
            current_rain = weather.get("rain", {}).get("1h", weather.get("rain", {}).get("3h", 120.5))
            current_pesticide = 1.5

            # Yield model expects "Crop, paddy" style names for rice — normalize
            crop_for_model = resolved_crop.capitalize()
            if crop_for_model.lower() == "rice":
                crop_for_model = "Rice, paddy"

            prediction = predict_yield_simple(
                yield_model,
                crop_for_model,
                current_rain,
                current_pesticide,
                current_temp
            )

            if crop_name:
                source_note = "(as you mentioned)"
            elif auto_predicted:
                source_note = "(auto-predicted for your location)"
            else:
                source_note = "(from your saved profile)"

            return (
                "🌾 **Crop Yield Prediction**:\n"
                f"📍 Location: ({lat:.4f}, {lon:.4f})\n"
                f"- Crop: {resolved_crop.capitalize()} {source_note}\n"
                f"- Temperature: {current_temp}°C\n"
                f"- Rainfall: {current_rain} mm\n"
                f"- Pesticide Level: {current_pesticide}\n\n"
                f"👉 **Predicted Yield**: {prediction}"
            )

        except Exception as e:
            return f"❌ Error during yield prediction: {str(e)}"

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not implemented")