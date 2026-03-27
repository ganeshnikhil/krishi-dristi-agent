import pandas as pd
from typing import Type
from pydantic import BaseModel
from langchain.tools import BaseTool
from app.models.loader import predict_crop  # ✅ Using your requested import

# ✅ Empty schema (matches your internal data pattern)
class EmptyInput(BaseModel):
    pass


class CropRecommendationInternalTool(BaseTool):
    name: str = "crop_recommendation_internal"
    description: str = (
        "Recommends the best crop to plant based on internal sensor data (NPK, pH, and climate). "
        "Does NOT require user input. "
        "Use this for real-time soil and climate-based crop suggestions."
    )
    args_schema: Type[BaseModel] = EmptyInput

    def _run(self) -> str:
        # ✅ Internal Sensor/Demo values
        # These represent the 7 features your Random Forest model expects
        n, p, k = 90, 42, 43
        temp = 20.8
        hum = 82.0
        ph = 6.5
        rain = 202.9

        # Path to the pipeline we just saved (the .pkl file)
        model_path = "app/models/crop_prediction_model.pkl"

        try:
            # ✅ Using your specific loader function
            # This function likely returns the label (e.g., 'rice')
            # and potentially the confidence score
            prediction, confidence = predict_crop(
                model_path,
                n, p, k, 
                temp, hum, ph, rain
            )

            return (
                "🌱 **Crop Recommendation Analysis**:\n"
                "----------------------------------\n"
                f"📍 **Soil Stats**: N:{n}, P:{p}, K:{k} | pH: {ph}\n"
                f"🌦️ **Climate**: {temp}°C | {hum}% Humidity | {rain}mm Rain\n\n"
                f"✅ **Suggested Crop**: {prediction.upper()}\n"
                f"📊 **Model Confidence**: {confidence:.2f}%"
            )

        except Exception as e:
            return f"❌ Error during crop recommendation: {str(e)}"

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not implemented")



