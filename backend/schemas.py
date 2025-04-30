from pydantic import BaseModel, Field, constr
from typing import List, Optional, Annotated

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: List[Message]
    stream: Optional[bool] = True

class ChatResponse(BaseModel):
    message: Message

class SessionCreate(BaseModel):
    title: str                              

class SessionOut(SessionCreate):
    id: int
    created_at: str

class MessageCreate(BaseModel):
    content: str
    session_id: int
    role: Optional[str] = "user"

class MessageOut(MessageCreate):
    id: int
