from fastapi import APIRouter, HTTPException, Query, Depends
from schemas import MessageCreate, MessageOut
from databases import SessionLocal
from models import Session, Message
from sqlalchemy.orm import Session as OrmSession
from typing import List
from databases import get_db

router = APIRouter(prefix="/messages")

@router.post("/", response_model=MessageOut, status_code=201)
def create_message(payload: MessageCreate, db: OrmSession = Depends(get_db)):
    session = db.query(Session).filter(Session.id == payload.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    message = Message(**payload.model_dump())
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

@router.get("/", response_model=List[MessageOut])
def get_messages(session_id: int = Query(...), db: OrmSession = Depends(get_db)):
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.messages
