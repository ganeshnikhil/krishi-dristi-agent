from langchain.tools import tool
from pydantic import BaseModel
from app.models.loader import predict_fertilizer


# class FertilizerInputSchema(BaseModel):
#     pass


# @tool(args_schema=FertilizerInputSchema)


def get_fertilizer_prediction() -> str:
    """Predict the most suitable fertilizer using internally available farm data."""
    sample_input = {
        "Temperature": 30.0,
        "Humidity": 60.0,
        "Moisture": 42.0,
        "Soil Type": "Sandy",
        "Crop Type": "Maize",
        "Nitrogen": 22,
        "Potassium": 0,
        "Phosphorous": 21,
    }
    
    weights_path = "app/models/fertilizer_bundle.pkl"

    prediction = predict_fertilizer(weights_path, sample_input)
    return f"Based on the collected data, the fertilizer recommended is: {prediction}"
