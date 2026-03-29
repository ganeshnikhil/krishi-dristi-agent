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
        "Automatically fetches current and 3-day weather forecasts for the farmer's GPS location. "
        "Use this to provide proactive agricultural advice (e.g., irrigation or harvest planning)."
    )
    args_schema: Type[BaseModel] = EmptyInput

    def _run(self) -> str:
        try:
            lat, lon = get_active_location()

            data = get_weather_data(lat, lon)

            # -----------------------------
            # SAFETY: ensure dict
            # -----------------------------
            if isinstance(data, str):
                import json
                data = json.loads(data)

            forecast = data.get("forecast", [])
            if not forecast:
                return "❌ No forecast data available"

            today = forecast[0]
            snapshots = today.get("snapshots", {})

            morning = snapshots.get("Morning", {})
            afternoon = snapshots.get("Afternoon", {})
            evening = snapshots.get("Evening", {})

            # Best representative values
            temp = afternoon.get("temp_C") or morning.get("temp_C") or "N/A"
            desc = today.get("condition", "N/A")
            rain = today.get("chance_of_rain_pct", 0)

            return (
                f"🌤️ Weather Report — {data.get('location','Unknown')}\n"
                f"📍 Coordinates: ({lat:.4f}, {lon:.4f})\n\n"
                f"🌡️ Temp (Afternoon): {temp} °C\n"
                f"🌧️ Rain Chance     : {rain}%\n"
                f"☁️ Condition       : {desc}\n\n"
                f"📅 Today Snapshot:\n"
                f"   🌅 Morning  : {morning.get('temp_C','N/A')}°C\n"
                f"   🌞 Afternoon: {afternoon.get('temp_C','N/A')}°C\n"
                f"   🌇 Evening  : {evening.get('temp_C','N/A')}°C"
            )


        except Exception as e:
            return f"❌ Unable to fetch weather data: {str(e)}"

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not implemented")
