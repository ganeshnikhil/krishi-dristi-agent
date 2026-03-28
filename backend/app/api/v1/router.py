from fastapi import APIRouter
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints import agent
from app.api.v1.endpoints import disaster


api_router = APIRouter(prefix="/api/v1")

# Include all routes here
api_router.include_router(auth_router, tags=["Auth"])
api_router.include_router(agent.router, prefix="/agent", tags=["Agent"])
# Disaster routes (NO extra /api/v1 here)
api_router.include_router(disaster.router, prefix="/disaster", tags=["Disaster"])