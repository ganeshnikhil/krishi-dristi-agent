
from langchain.tools import tool
from app.models.loader import predict_yield_simple


@tool
def get_crop_prediction() -> str:
    """
    Retrieve internal environmental data and predict the most suitable crop
    for the current conditions without requiring user input.
    """
    current_temp = 28.4   # Celsius
    current_rain = 120.5  # mm
    crop_name = "Rice"
    current_pesticide = 1.5
    weights_path = "app/models/india_crop_yield_model.pkl"
    try:
        prediction = predict_yield_simple(
            weights_path,
            crop_name,
            current_rain,
            current_pesticide,
            current_temp
        )

        return (
            f"Analysis complete: based on a temperature of {current_temp}°C "
            f"and rainfall of {current_rain} mm, the best crop to grow is: {prediction}"
        )

    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"