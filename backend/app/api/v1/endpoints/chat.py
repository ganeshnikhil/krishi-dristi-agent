# from fastapi import APIRouter, HTTPException, Header
# from pydantic import BaseModel
# from langchain_core.messages import HumanMessage
# from langgraph.checkpoint.sqlite import SqliteSaver
# import sqlite3
# import os
#
# from app.agents.online_farmer_agent import get_sarvam_llm, create_farmer_agent
# from app.services.auth_service import decode_token
# from app.core.user_context import set_current_user
#
# router = APIRouter(prefix="/chat", tags=["Chat"])
#
# DB_PATH = "app/data/farmer_data.db"
# _agent = None   # Lazy init — created once per process
#
#
# def _get_or_create_agent():
#     """Create the LangGraph agent on first call and reuse it."""
#     global _agent
#     if _agent is None:
#         llm = get_sarvam_llm(os.getenv("SARVAM105_MODEL_NAME", "sarvam-105b"))
#         # SqliteSaver needs a raw sqlite3 connection (not a context manager)
#         conn = sqlite3.connect(DB_PATH, check_same_thread=False)
#         checkpointer = SqliteSaver(conn)
#         _agent = create_farmer_agent(llm, checkpointer)
#     return _agent
#
#
# def _get_username_from_token(authorization: str) -> str:
#     if not authorization or not authorization.startswith("Bearer "):
#         raise HTTPException(status_code=401, detail="Missing or invalid Authorization header.")
#     token = authorization.split(" ", 1)[1]
#     payload = decode_token(token)
#     if not payload:
#         raise HTTPException(status_code=401, detail="Invalid or expired token.")
#     return payload["sub"]
#
#
# class ChatRequest(BaseModel):
#     message: str
#
#
# class ChatResponse(BaseModel):
#     reply: str
#     username: str
#
#
# @router.post("/", response_model=ChatResponse, summary="Send a message to the Krishi AI Agent")
# def chat(body: ChatRequest, authorization: str = Header(...)):
#     """
#     Send a farming question to the AI Agent.
#     The agent will automatically use the farmer's saved GPS location for real-time data.
#
#     **Header required**: `Authorization: Bearer <access_token>`
#     """
#     username = _get_username_from_token(authorization)
#
#     # ✅ Set the current user so all tools know whose location to use
#     set_current_user(username)
#
#     agent = _get_or_create_agent()
#     config = {"configurable": {"thread_id": username}}
#
#     try:
#         response = agent.invoke(
#             {"messages": [HumanMessage(content=body.message)]},
#             config=config
#         )
#         reply = response["messages"][-1].content
#         return ChatResponse(reply=reply, username=username)
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver

import sqlite3
import os
import threading

from app.agents.online_farmer_agent import get_sarvam_llm, create_farmer_agent
from app.services.auth_service import decode_token
from app.core.user_context import set_current_user

# ─────────────────────────────────────────────────────────────
router = APIRouter(prefix="/chat", tags=["Chat"])

DB_PATH = "app/data/farmer_data.db"

_agent = None
_conn = None
_db_lock = threading.Lock()


# ─────────────────────────────────────────────────────────────
# ✅ SAFE DB INITIALIZATION
def _init_db():
    global _conn

    if _conn is not None:
        return _conn

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)

        # 🔥 Critical for preventing corruption
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")

        _conn = conn
        return conn

    except sqlite3.DatabaseError:
        print("⚠️ DB corrupted. Recreating...")

        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)

        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL;")

        _conn = conn
        return conn


# ─────────────────────────────────────────────────────────────
# ✅ AGENT INITIALIZATION (Lazy Singleton)
def _get_or_create_agent():
    global _agent

    if _agent is None:
        llm = get_sarvam_llm(os.getenv("SARVAM105_MODEL_NAME", "sarvam-105b"))

        conn = _init_db()
        checkpointer = SqliteSaver(conn)

        _agent = create_farmer_agent(llm, checkpointer)

    return _agent


# ─────────────────────────────────────────────────────────────
# ✅ AUTH HANDLING
def _get_username_from_token(authorization: str) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing/Invalid Authorization header")

    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid/Expired token")

    return payload["sub"]


# ─────────────────────────────────────────────────────────────
# ✅ REQUEST / RESPONSE MODELS
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"


class ChatResponse(BaseModel):
    reply: str
    username: str

class ChatHistoryOut(BaseModel):
    messages: list[dict]


# ─────────────────────────────────────────────────────────────
# ✅ MAIN CHAT ENDPOINT
@router.post("/", response_model=ChatResponse)
def chat(body: ChatRequest, authorization: str = Header(...)):
    username = _get_username_from_token(authorization)

    # Set user context for tools
    set_current_user(username)

    agent = _get_or_create_agent()
    config = {"configurable": {"thread_id": username}}

    try:
        # 🔐 Prevent concurrent DB writes
        with _db_lock:
            response = agent.invoke(
                {"messages": [HumanMessage(content=body.message)]},
                config=config
            )

        reply = response["messages"][-1].content
        session_id = body.session_id or "default"

        # ✅ Persist chat to MongoDB grouped by username AND session_id
        from app.db.session import get_db
        from datetime import datetime
        db = get_db()
        db.chat_history.update_one(
            {"username": username, "session_id": session_id},
            {
                "$push": {
                    "messages": {
                        "user_message": body.message,
                        "agent_reply": reply,
                        "timestamp": datetime.utcnow()
                    }
                }
            },
            upsert=True
        )

        return ChatResponse(reply=reply, username=username)

    except Exception as e:
        error_msg = str(e)

        # 💣 Handle DB corruption automatically
        if "database disk image is malformed" in error_msg:
            if os.path.exists(DB_PATH):
                os.remove(DB_PATH)

            global _agent, _conn
            _agent = None
            _conn = None

            raise HTTPException(
                status_code=500,
                detail="Database corrupted. Reset done. Please retry."
            )

        raise HTTPException(
            status_code=500,
            detail=f"Agent error: {error_msg}"
        )


@router.get("/history", response_model=ChatHistoryOut, summary="Retrieve chat history from MongoDB")
def get_chat_history(authorization: str = Header(...), session_id: Optional[str] = None):
    """Fetch past interactions. If session_id provided, fetch that specific session."""
    username = _get_username_from_token(authorization)
    from app.db.session import get_db
    db = get_db()
    
    query = {"username": username}
    if session_id:
        query["session_id"] = session_id
        doc = db.chat_history.find_one(query)
        docs = [doc] if doc else []
    else:
        # Return all sessions for this user
        docs = db.chat_history.find(query).sort("session_id", 1)
    
    history = []
    for doc in docs:
        if "messages" in doc:
            for m in doc["messages"]:
                history.append({
                    "role": "user",
                    "content": m["user_message"],
                    "timestamp": m["timestamp"],
                    "session_id": doc.get("session_id", "default")
                })
                history.append({
                    "role": "assistant",
                    "content": m["agent_reply"],
                    "timestamp": m["timestamp"],
                    "session_id": doc.get("session_id", "default")
                })
    
    return ChatHistoryOut(messages=history)