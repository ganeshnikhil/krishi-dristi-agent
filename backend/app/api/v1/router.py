from fastapi import APIRouter
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints import agent
from app.api.v1.endpoints import disaster

from app.api.v1.endpoints.user import router as user_router
from app.api.v1.endpoints.chat import router as chat_router
from app.api.v1.endpoints import username
from app.api.v1.endpoints import keyword



api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(chat_router)

api_router.include_router(disaster.router)
api_router.include_router(username.router)
api_router.include_router(keyword.router)