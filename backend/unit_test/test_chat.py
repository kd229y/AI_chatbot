from fastapi.testclient import TestClient
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app
from databases import SessionLocal
from models import Session as ChatSession, Message
from routers.chat import OLLAMA_API
client = TestClient(app)

db = SessionLocal()

db.query(Message).delete()
db.query(ChatSession).delete()
db.commit()

def test_session_create_success():
    response = client.post(
        "/sessions/",
        json={
            "title": "This is a test session."
        }
    )
    assert response.status_code == 201
    return response.json()["id"]
def test_session_create_failure():
    response = client.post(
        "/sessions/",
        json={
            "title": ""  
        }
    )
    assert response.status_code == 422
def test_session_list():
    response = client.get("/sessions/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
def test_session_get():
    session_id = test_session_create_success()
    response = client.get(f"/sessions/{session_id}")
    assert response.status_code == 200
    assert response.json()["id"] == session_id

def test_session_update():
    session_id = test_session_create_success()
    response = client.put(
        f"/sessions/{session_id}",
        json={
            "title": "Updated Session"
        }
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Session"

def test_session_delete():
    session_id = test_session_create_success()
    response = client.delete(f"/sessions/{session_id}")
    assert response.status_code == 204
    response = client.get(f"/sessions/{session_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"
def test_message_create_success():
    session_id = test_session_create_success()
    response = client.post(
        "/messages/",
        json={
            "session_id": session_id,
            "role": "user",
            "content": "Hello, how are you?"
        }
    )
    assert response.status_code == 201
    return response.json()["id"]
def test_message_create_failure():
    response = client.post(
        "/messages/",
        json={
            "session_id": 99999,  # Non-existent session ID
            "role": "user",
            "content": "Hello, how are you?"
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"
def test_message_get_all():
    session_id = test_session_create_success()

    payload = {
        "session_id": session_id,
        "role": "user",
        "content": "Hello from test"
    }
    response_create = client.post("/messages/", json=payload)
    assert response_create.status_code == 201
    message_id = response_create.json()["id"]

    response = client.get(f"/messages/?session_id={session_id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(msg["id"] == message_id for msg in data)

def chat_endpoint_success():
    session_id = test_session_create_success()
    response = client.post(
        "/chat",
        json={
            "model": "ollama2",
            "messages": [
                {
                    "role": "user",
                    "content": "Hello, how are you?"
                }
            ],
            "session_id": session_id
        }
    )
    assert response.status_code == 200
    assert response.json()["message"]["role"] == "assistant"
    assert response.json()["message"]["content"] == "This is a mock response from the Ollama API."
def test_chat_endpoint_failure():
    response = client.post(
        "/chat",
        json={
            "model": "ollama2",
            "messages": [
                {
                    "role": "user",
                    "content": "Hello, how are you?"
                }
            ]
        }
    )
    assert response.status_code == 422

