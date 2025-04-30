from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(30), nullable=False)
    created_at = Column(DateTime, default=datetime.now(datetime.timezone.utc))
    messages = relationship("Message", back_populates="session")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    role = Column(String(10), default="user")
    session_id = Column(Integer, ForeignKey("sessions.id"))
    session = relationship("Session", back_populates="messages")
