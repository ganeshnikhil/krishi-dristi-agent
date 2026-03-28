from fastapi import APIRouter, HTTPException, Header, status
from pydantic import BaseModel
from app.core.user_context import set_user_location
from app.services.auth_service import decode_token

router = APIRouter(prefix="/user", tags=["User"])


class LocationUpdate(BaseModel):
    lat: float
    lon: float


def _get_username_from_token(authorization: str) -> str:
    """Helper: extract username from 'Bearer <token>' header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header.")
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    return payload["sub"]   # 'sub' holds the username


@router.post("/location", status_code=200, summary="Save the farmer's GPS coordinates")
def update_location(body: LocationUpdate, authorization: str = Header(...)):
    """
    Called once after the farmer logs in to save their GPS coordinates.
    All AI tools will now use these coordinates for real-time data.

    **Header required**: `Authorization: Bearer <access_token>`
    """
    username = _get_username_from_token(authorization)
    set_user_location(username, body.lat, body.lon)
    return {
        "message": f"✅ Location saved for {username}",
        "lat": body.lat,
        "lon": body.lon,
    }
