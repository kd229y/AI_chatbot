from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from schemas import ChatRequest, ChatResponse
from databases import SessionLocal
from models import Session, Message
from sqlalchemy.orm import Session as OrmSession

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest, session_id: Optional[int] = Query(None), db: OrmSession = Depends(SessionLocal)):
    history = []
    if session_id:
        chat_session = db.query(Session).filter(Session.id == session_id).first()
        if not chat_session:
            raise HTTPException(status_code=404, detail="Session not found")
        history = [{"role": m.role, "content": m.content} for m in chat_session.messages]

    messages = history + [m.model_dump() for m in payload.messages]
    
    # 模擬呼叫 ollama API
    reply = {"role": "assistant", "content": "This is a response."}

    return {"message": reply}
