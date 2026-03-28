from pydantic import BaseModel

class AgentResponse(BaseModel):
    response: str
    route: str



from pydantic import BaseModel
from typing import List, Optional

class DisasterEvent(BaseModel):
    date: Optional[str]
    event_name: Optional[str]
    proximity_severity_level: Optional[str]
    default_alert_levels: Optional[str]


class DisasterResponse(BaseModel):
    message: str
    events: List[DisasterEvent]
    
