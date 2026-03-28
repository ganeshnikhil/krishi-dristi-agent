from fastapi import APIRouter
from app.schemas.request import AgentRequest
from app.schemas.response import AgentResponse
from app.core.dependencies import agent_service

router = APIRouter()

@router.post("/run", response_model=AgentResponse)
async def run_agent(request: AgentRequest):

    result, route = await agent_service.run(
        user_query=request.query,
        user_id=request.user_id
    )

    return AgentResponse(
        response=result,
        route=route
    )
