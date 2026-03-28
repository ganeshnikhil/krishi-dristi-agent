from typing import Type, Optional
from pydantic import BaseModel, Field
from pathlib import Path
from langchain.tools import BaseTool
from app.models.loader import predict_fertilizer, predict_crop
from app.services.weather_service import get_weather_data
from app.services.npk_ph_level import get_soil_data_for_state
from app.core.user_context import (
    get_active_location, get_active_state, get_active_crop,
    get_current_user, set_user_crop
)


# ── Input schema ─────────────────────────────────────────────────────────────
class FertilizerInput(BaseModel):
    crop_type: Optional[str] = Field(
        default=None,
        description="The crop type (e.g., 'Rice', 'Wheat'). Leave empty to auto-detect."
    )


class FertilizerPredictionTool(BaseTool):
    name: str = "fertilizer_prediction_internal"
    description: str = (
        "Predicts the most suitable fertilizer using real-time weather data for the farmer's GPS location. "
        "Automatically reads the farmer's last predicted crop from the database. "
        "If no crop is in the database yet, it runs the crop prediction automatically first. "
        "Only pass 'crop_type' if the user explicitly mentions a crop name in their message."
    )
    args_schema: Type[BaseModel] = FertilizerInput

    def _run(self, crop_type: Optional[str] = None) -> str:
        lat, lon = get_active_location()
        fertilizer_model  = str(Path(__file__).resolve().parent.parent / "models" / "fertilizer_bundle.pkl")
        crop_model        = str(Path(__file__).resolve().parent.parent / "models" / "crop_prediction_model.pkl")

        # ── Resolve crop ──────────────────────────────────────────────────────
        # Priority: 1) user passed crop_type in message
        #           2) last predicted crop saved in DB for this user
        #           3) auto-run crop prediction now and save result
        auto_predicted = False
        resolved_crop  = crop_type or get_active_crop()

        if not resolved_crop:
            # No crop in DB — predict it automatically right now
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

                # Save to DB so future calls don't need to re-predict
                user = get_current_user()
                if user:
                    try:
                        set_user_crop(user, resolved_crop)
                        print(f"[DB] ✅ Auto-saved predicted crop '{resolved_crop}' for user '{user}'")
                    except Exception as db_err:
                        print(f"[DB] ⚠️ Could not save crop: {db_err}")

            except Exception as crop_err:
                return (
                    f"❌ Could not auto-predict crop: {crop_err}\n"
                    "Please ask 'what crop should I grow?' first, or say e.g. 'recommend fertilizer for wheat'."
                )

        try:
            # Fetch real weather for the fertilizer model
            weather     = get_weather_data(lat, lon)
            temperature = weather.get("main", {}).get("temp", 30.0)
            humidity    = weather.get("main", {}).get("humidity", 60.0)

            state = get_active_state()
            soil_data = get_soil_data_for_state(state) if state else None
            
            n_val = soil_data["N"] if soil_data else 22
            p_val = soil_data["P"] if soil_data else 21
            k_val = soil_data["K"] if soil_data else 0

            sample_input = {
                "Temperature":  temperature,
                "Humidity":     humidity,
                "Moisture":     42.0,
                "Soil Type":    "Sandy",
                "Crop Type":    resolved_crop.capitalize(),
                "Nitrogen":     n_val,
                "Potassium":    k_val,
                "Phosphorous":  p_val,
            }

            prediction = predict_fertilizer(fertilizer_model, sample_input)

            if crop_type:
                source_note = "(as you mentioned)"
            elif auto_predicted:
                source_note = "(auto-predicted for your location)"
            else:
                source_note = "(from your saved profile)"

            return (
                "🌱 **Fertilizer Recommendation**:\n"
                f"📍 Location: ({lat:.4f}, {lon:.4f})\n"
                f"- Crop: {resolved_crop.capitalize()} {source_note}\n"
                f"- Temperature: {temperature}°C | Humidity: {humidity}%\n"
                f"- N: {sample_input['Nitrogen']} | P: {sample_input['Phosphorous']} | K: {sample_input['Potassium']}\n\n"
                f"👉 **Recommended Fertilizer**: {prediction}"
            )

        except Exception as e:
            return f"❌ Error during fertilizer prediction: {str(e)}"

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not implemented")