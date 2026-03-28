from pydantic import BaseModel
from typing import Optional

class AgentRequest(BaseModel):
    query: str
    user_id: str
    language: Optional[str] = "en"
    mode: Optional[str] = "auto"   # auto | tool | chat


class DisasterRequest(BaseModel):
    lat: float
    lng: float
    