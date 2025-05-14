from fastapi import APIRouter, HTTPException, Query, Path, Depends
from schemas import SessionCreate, SessionOut
from databases import get_db
from models import Session
from sqlalchemy.orm import Session as OrmSession
from typing import List
from datetime import datetime as dt

router = APIRouter(prefix="/sessions")

@router.post("/", response_model=SessionOut, status_code=201)
def create_session(payload: SessionCreate, db: OrmSession = Depends(get_db)):
    new_session = Session(title=payload.title)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@router.get("/", response_model=List[SessionOut])
def list_sessions(offset: int = 0, limit: int = 100, db: OrmSession = Depends(get_db)):
    return db.query(Session).offset(offset).limit(limit).all()

@router.get("/{id}", response_model=SessionOut)
def get_session(id: int = Path(...), db: OrmSession = Depends(get_db)):
    session = db.query(Session).filter(Session.id == id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.put("/{id}", response_model=SessionOut)
def update_session(id: int, payload: SessionCreate, db: OrmSession = Depends(get_db)):
    session = db.query(Session).filter(Session.id == id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session.title = payload.title
    db.commit()
    db.refresh(session)
    return session

@router.delete("/{id}", status_code=204)
def delete_session(id: int, db: OrmSession = Depends(get_db)):
    session = db.query(Session).filter(Session.id == id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()
