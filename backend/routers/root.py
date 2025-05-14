
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from schemas import ChatRequest, ChatResponse
from databases import SessionLocal
from models import Session, Message
from sqlalchemy.orm import Session as OrmSession
import requests

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Chat API is running"}