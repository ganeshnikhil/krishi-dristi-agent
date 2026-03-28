from fastapi import APIRouter, HTTPException
from app.schemas.request import DisasterRequest
from app.schemas.response import DisasterResponse, DisasterEvent
from app.services.disaster_alert import fetch_disaster

router = APIRouter()


@router.post("/disaster", response_model=DisasterResponse)
def get_disaster_alert(payload: DisasterRequest):
    try:
        data = fetch_disaster(payload.lat, payload.lng)

        results = data.get("result", [])

        events = [
            DisasterEvent(
                date=e.get("date"),
                event_name=e.get("event_name"),
                proximity_severity_level=e.get("proximity_severity_level"),
                default_alert_levels=e.get("default_alert_levels"),
            )
            for e in results
        ]

        return DisasterResponse(
            message="success",
            events=events
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
    
