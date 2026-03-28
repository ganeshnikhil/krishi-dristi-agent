from fastapi import APIRouter, HTTPException
from bson import ObjectId
from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.db.session import get_db
from app.services.keypoint_gem import get_keywords_from_gemini

router = APIRouter()

# class KeywordAnalysisResponse(BaseModel):
#     session_id: str
#     username: str
#     keywords: List[str]

# @router.get("/keywords/{sid}", response_model=KeywordAnalysisResponse)
# async def get_and_store_keywords(sid: str):
#     db = get_db()
    
#     # 1. Fetch original chat using the SID (Object ID) provided in the URL
#     try:
#         obj_id = ObjectId(sid)
#         doc = db.chat_history.find_one({"_id": obj_id})
#     except Exception:
#         raise HTTPException(status_code=400, detail="Invalid Object ID format")

#     if not doc:
#         raise HTTPException(status_code=404, detail="Original session not found")

#     # 2. Extract and Flatten messages for Gemini
#     # We combine user messages and agent replies into one block of text
#     messages = [f"{m.get('user_message')} {m.get('agent_reply')}" for m in doc.get("messages", [])]
#     conversation_dump = " ".join(messages)

#     # 3. Get Keywords from Gemini Service (keypoint_gem.py)
#     try:
#         keyword_list = get_keywords_from_gemini(conversation_dump)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"AI Error: {str(e)}")

#     # 4. Prepare data for the NEW collection: 'keyword'
#     # This entry will get its own unique _id automatically
#     analysis_entry = {
#         "session_id": doc.get("session_id"), # The UUID string from your data
#         "username": doc.get("username"),
#         "keywords": keyword_list,
#         "timestamp": datetime.utcnow()
#     }

#     # 5. Insert into the 'keyword' collection
#     db.keyword.insert_one(analysis_entry)

#     # 6. Return response to the user
#     return KeywordAnalysisResponse(
#         session_id=analysis_entry["session_id"],
#         username=analysis_entry["username"],
#         keywords=analysis_entry["keywords"]
#     )
 
@router.get("/keywords/{sid}")
async def get_and_store_keywords(sid: str):
    db = get_db()
    
    # 1. First, try to find the document by the string session_id (the UUID)
    doc = db.chat_history.find_one({"session_id": sid})

    # 2. If not found, only THEN try to treat it as a BSON ObjectId
    if not doc:
        try:
            if len(sid) == 24: # Only try ObjectId if it looks like a hex string
                doc = db.chat_history.find_one({"_id": ObjectId(sid)})
        except Exception:
            pass

    # 3. If still not found, raise the 404
    if not doc:
        raise HTTPException(status_code=404, detail="Session not found in history")

    # --- Rest of your logic ---
    messages = [f"{m.get('user_message')} {m.get('agent_reply')}" for m in doc.get("messages", [])]
    conversation_dump = " ".join(messages)
    
    keyword_list = get_keywords_from_gemini(conversation_dump)

    analysis_entry = {
        "session_id": doc.get("session_id"),
        "username": doc.get("username"),
        "keywords": keyword_list,
        "timestamp": datetime.utcnow()
    }
    
    # Insert into the 'keyword' collection
    db.keyword.insert_one(analysis_entry)

    return {
        "session_id": analysis_entry["session_id"],
        "keywords": keyword_list
    }
