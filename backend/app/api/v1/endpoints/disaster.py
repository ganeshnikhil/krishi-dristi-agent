from fastapi import APIRouter, HTTPException
from app.schemas.request import DisasterRequest
from app.schemas.response import DisasterResponse, DisasterEvent
from app.services.disaster_alert import get_latest_disaster

router = APIRouter()


@router.post("/disaster", response_model=DisasterResponse)
def get_disaster_alert(payload: DisasterRequest):
    try:
        data = get_latest_disaster(payload.lat, payload.lng)

        # Handle error dictionary from service
        if isinstance(data, dict) and data.get("error"):
            raise HTTPException(status_code=502, detail=data.get("message", "Upstream API error"))

        events = [
            DisasterEvent(
                date=e.get("date"),
                event_name=e.get("event_name"),
                proximity_severity_level=e.get("proximity_severity_level"),
                default_alert_levels=e.get("default_alert_levels"),
            )
            for e in data
        ]

        return DisasterResponse(
            message="success",
            events=events
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
    
