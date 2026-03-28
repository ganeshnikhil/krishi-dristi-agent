from pydantic import BaseModel

class AgentResponse(BaseModel):
    response: str
    route: str
    
    
