from typing import Type
from pydantic import BaseModel
from langchain.tools import BaseTool
from app.services.soil_service import fetch_soil_data


class EmptyInput(BaseModel):
    pass


class SoilInfoTool(BaseTool):
    name: str = "soil_data_internal"
    description: str = (
        "Fetches soil data (temperature and moisture) for the farmer's registered polygon. "
        "Does NOT require user input. "
        "Use this when soil conditions are needed for farming decisions."
    )
    args_schema: Type[BaseModel] = EmptyInput

    def _run(self) -> str:
        try:
            data = fetch_soil_data()

            dt       = data.get("dt", "N/A")
            t0       = data.get("t0", "N/A")
            t10      = data.get("t10", "N/A")
            moisture = data.get("moisture", "N/A")

            # Convert from Kelvin to Celsius if values look like Kelvin (>200)
            t0_c  = round(t0 - 273.15, 1)  if isinstance(t0, (int, float))  else t0
            t10_c = round(t10 - 273.15, 1) if isinstance(t10, (int, float)) else t10

            return (
                "🌱 **Soil Data Analysis**:\n"
                f"- Time (UTC): {dt}\n"
                f"- Surface Temperature  : {t0_c} °C\n"
                f"- Temperature at 10cm  : {t10_c} °C\n"
                f"- Soil Moisture        : {moisture} m³/m³"
            )

        except Exception as e:
            return f"❌ Unable to fetch soil data: {str(e)}"

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not implemented")
