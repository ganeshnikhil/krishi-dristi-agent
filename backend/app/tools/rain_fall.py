from typing import Type
from pydantic import BaseModel
from pathlib import Path
from langchain.tools import BaseTool
from app.services.rainfall_service import get_rainfall_data
from app.core.user_context import get_active_location


class EmptyInput(BaseModel):
    pass


class RainfallPredictionTool(BaseTool):
    name: str = "rainfall_prediction_internal"
    description: str = (
        "Provides rainfall data for the farmer's GPS location using a regional rainfall dataset. "
        "Does NOT require user input. "
        "Use this when rainfall information is needed."
    )
    args_schema: Type[BaseModel] = EmptyInput

    def _run(self) -> str:
        
        lat, lon = get_active_location()

        # fallback to Dehradun if invalid
        if lat is None or lon is None:
            lat, lon = 30.3165, 78.0322
        csv_file = str(Path(__file__).resolve().parent.parent / "data" / "rain_fall_distribution.csv")

        try:
            result = get_rainfall_data(csv_file, (lat, lon))

            return (
                "🌧️ **Rainfall Analysis**:\n"
                f"📍 Location Coordinates: ({lat:.4f}, {lon:.4f})\n\n"
                f"👉 Estimated Rainfall: {result}"
            )

        except Exception as e:
            return f"❌ Error while fetching rainfall data: {str(e)}"

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not implemented")
