from fastapi import FastAPI
from routers import chat, sessions, messages, root
from databases import init_db
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Chat API with Ollama")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

init_db()

app.include_router(root.router)
app.include_router(chat.router)
app.include_router(sessions.router)
app.include_router(messages.router)

