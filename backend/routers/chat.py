from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from schemas import ChatRequest, ChatResponse
from databases import get_db
from models import Session, Message
from sqlalchemy.orm import Session as OrmSession
import requests

router = APIRouter()
OLLAMA_API = "http://10.23.0.1:11434/api/generate"

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest, session_id: Optional[int] = Query(None), db: OrmSession = Depends(get_db)):
    history = []
    if not session_id:
        raise HTTPException(status_code=422, detail="Session ID is required")
    if session_id:
        chat_session = db.query(Session).filter(Session.id == session_id).first()
        if not chat_session:
            raise HTTPException(status_code=404, detail="Session not found")
        history = [{"role": m.role, "content": m.content} for m in chat_session.messages]
    #if choosen model is not supported
    if payload.model not in ["ollama2", "llama2", "llama3", "llama3-13b", "llama3-70b"]:
        raise HTTPException(status_code=400, detail="Model not supported")
    messages = history + [m.model_dump() for m in payload.messages]
    model = payload.model
    #TODO: need to implement ollama api
    '''reply = requests.post(OLLAMA_API, json={
        "model": model,
        "messages": messages
    })
    ollama_data = reply.json()
    reply = ollama_data.get("message")'''
    reply= {
        "role": "assistant",
        "content": "This is a mock response from the Ollama API."
    }
    if not reply:
        raise HTTPException(status_code=500, detail="Ollama response missing message")
    
    return {"message": reply}
