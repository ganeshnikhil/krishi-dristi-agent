from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import os

from app.agents.online_farmer_agent import get_sarvam_llm, create_farmer_agent
from app.services.auth_service import decode_token
from app.core.user_context import set_current_user

router = APIRouter(prefix="/chat", tags=["Chat"])

DB_PATH = "app/data/farmer_data.db"
_agent = None   # Lazy init — created once per process


def _get_or_create_agent():
    """Create the LangGraph agent on first call and reuse it."""
    global _agent
    if _agent is None:
        llm = get_sarvam_llm(os.getenv("SARVAM105_MODEL_NAME", "sarvam-105b"))
        # SqliteSaver needs a raw sqlite3 connection (not a context manager)
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        checkpointer = SqliteSaver(conn)
        _agent = create_farmer_agent(llm, checkpointer)
    return _agent


def _get_username_from_token(authorization: str) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header.")
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    return payload["sub"]


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    username: str


@router.post("/", response_model=ChatResponse, summary="Send a message to the Krishi AI Agent")
def chat(body: ChatRequest, authorization: str = Header(...)):
    """
    Send a farming question to the AI Agent.
    The agent will automatically use the farmer's saved GPS location for real-time data.

    **Header required**: `Authorization: Bearer <access_token>`
    """
    username = _get_username_from_token(authorization)

    # ✅ Set the current user so all tools know whose location to use
    set_current_user(username)

    agent = _get_or_create_agent()
    config = {"configurable": {"thread_id": username}}

    try:
        response = agent.invoke(
            {"messages": [HumanMessage(content=body.message)]},
            config=config
        )
        reply = response["messages"][-1].content
        return ChatResponse(reply=reply, username=username)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")
