from typing import Type
from pydantic import BaseModel
from langchain.tools import BaseTool
from app.services.weather_service import get_weather_data
from app.core.user_context import get_active_location


class EmptyInput(BaseModel):
    pass


class WeatherInfoTool(BaseTool):
    name: str = "weather_data_internal"
    description: str = (
        "Fetches real-time weather information (temperature, humidity, rain, etc.) for the farmer's GPS location. "
        "Does NOT require user input. "
        "Use this when current weather conditions are needed."
    )
    args_schema: Type[BaseModel] = EmptyInput

    def _run(self) -> str:
        lat, lon = get_active_location()

        try:
            data = get_weather_data(lat, lon)

            temp     = data.get("main", {}).get("temp", "N/A")
            humidity = data.get("main", {}).get("humidity", "N/A")
            desc     = data.get("weather", [{}])[0].get("description", "N/A")
            wind     = data.get("wind", {}).get("speed", "N/A")
            city     = data.get("name", f"({lat:.3f}, {lon:.3f})")
            rain_1h  = data.get("rain", {}).get("1h", 0)

            return (
                f"🌤️ **Weather Report** — {city}\n"
                f"📍 Coordinates: ({lat:.4f}, {lon:.4f})\n\n"
                f"🌡️ Temperature : {temp} °C\n"
                f"💧 Humidity    : {humidity} %\n"
                f"🌧️ Rain (1h)   : {rain_1h} mm\n"
                f"💨 Wind Speed  : {wind} m/s\n"
                f"☁️ Conditions  : {desc.capitalize()}"
            )

        except Exception as e:
            return f"❌ Unable to fetch weather data: {str(e)}"

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not implemented")
