from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from schemas import ChatRequest, ChatResponse
from databases import get_db
from models import Session, Message
from sqlalchemy.orm import Session as OrmSession
import requests
from fastapi.responses import JSONResponse

router = APIRouter()
OLLAMA_API = "http://192.168.32.221:11434/api/generate"

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest, session_id: Optional[int] = Query(None), db: OrmSession = Depends(get_db)):
    history = []
    if not session_id:
        raise HTTPException(status_code=422, detail="Session ID is required")

    chat_session = db.query(Session).filter(Session.id == session_id).first()
    if not chat_session:
        raise HTTPException(status_code=404, detail="Session not found")

    history = [{"role": m.role, "content": m.content} for m in chat_session.messages]

    if payload.model not in ["llama3.2"]:
        raise HTTPException(status_code=400, detail="Model not supported")

    messages = history + [m.model_dump() for m in payload.messages]
    prompt_text = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
    
    try:
        response = requests.post(OLLAMA_API, json={
            "model": payload.model,
            "prompt": prompt_text,
            "stream": False  # 禁用 stream，方便 json() 使用
        })
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")
    except ValueError:
        raise HTTPException(status_code=500, detail="Failed to parse Ollama response")

    if not data.get("response"):
        raise HTTPException(status_code=500, detail="Ollama response missing 'response' field")

    # 可選：將使用者訊息與回覆存入 DB
    for msg in payload.messages:
        db.add(Message(session_id=session_id, role=msg.role, content=msg.content))

    db.add(Message(session_id=session_id, role="assistant", content=data["response"]))
    db.commit()

    return {"message": {"role": "assistant", "content": data["response"]}}

