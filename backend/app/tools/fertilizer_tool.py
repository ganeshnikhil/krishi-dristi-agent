# from langchain.tools import tool
# from pydantic import BaseModel
# from app.models.loader import predict_fertilizer


# # class FertilizerInputSchema(BaseModel):
# #     pass


# # @tool(args_schema=FertilizerInputSchema)

# @tool
# def get_fertilizer_prediction() -> str:
#     """Predict the most suitable fertilizer using internally available farm data."""
#     sample_input = {
#         "Temperature": 30.0,
#         "Humidity": 60.0,
#         "Moisture": 42.0,
#         "Soil Type": "Sandy",
#         "Crop Type": "Maize",
#         "Nitrogen": 22,
#         "Potassium": 0,
#         "Phosphorous": 21,
#     }
    
#     weights_path = "app/models/fertilizer_bundle.pkl"

#     prediction = predict_fertilizer(weights_path, sample_input)
#     return f"Based on the collected data, the fertilizer recommended is: {prediction}"


from typing import Type
from pydantic import BaseModel
from pathlib import Path

from langchain.tools import BaseTool
from app.models.loader import predict_fertilizer
from app.services.soil_type import get_soil_type

# ✅ Empty schema (no user input required)
class EmptyInput(BaseModel):
    pass


class FertilizerPredictionTool(BaseTool):
    name: str = "fertilizer_prediction_internal"
    description: str = (
        "Predicts the most suitable fertilizer using internal farm data such as "
        "temperature, humidity, soil type, crop type, and nutrient levels. "
        "Does NOT require user input."
    )
    args_schema: Type[BaseModel] = EmptyInput
    
    def _run(self) -> str:
        # ✅ Hardcoded demo data
        lat = 28.6139
        lon = 77.2090
        sample_input = {
            "Temperature": 30.0,
            "Humidity": 60.0,
            "Moisture": 42.0,
            "Soil Type": get_soil_type(lat , lon),
            "Crop Type": "Maize",
            "Nitrogen": 22,
            "Potassium": 0,
            "Phosphorous": 21,
        }

        weights_path = str(Path(__file__).resolve().parent.parent / "models" / "fertilizer_bundle.pkl")

        try:
            prediction = predict_fertilizer(weights_path, sample_input)

            return (
                "🌱 Fertilizer Recommendation Result:\n"
                f"- Crop: {sample_input['Crop Type']}\n"
                f"- Soil Type: {sample_input['Soil Type']}\n"
                f"- Temperature: {sample_input['Temperature']}°C\n"
                f"- Humidity: {sample_input['Humidity']}%\n"
                f"- Moisture: {sample_input['Moisture']}\n"
                f"- Nitrogen: {sample_input['Nitrogen']}\n"
                f"- Phosphorous: {sample_input['Phosphorous']}\n"
                f"- Potassium: {sample_input['Potassium']}\n\n"
                f"👉 Recommended Fertilizer: {prediction}"
            )

        except Exception as e:
            return f"❌ Error during fertilizer prediction: {str(e)}"

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not implemented")
    
    
    