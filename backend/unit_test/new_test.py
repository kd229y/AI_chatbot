import pytest
from fastapi.testclient import TestClient
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from databases import SessionLocal
from models import Session as ChatSession, Message

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_db():
    db = SessionLocal()
    db.query(Message).delete()
    db.query(ChatSession).delete()
    db.commit()
    db.close()

def create_session(title="Test Session"):
    response = client.post("/sessions/", json={"title": title})
    assert response.status_code == 201
    return response.json()["id"]

def test_session_create_success():
    session_id = create_session("My New Session")
    assert isinstance(session_id, int)

def test_session_create_failure():
    response = client.post("/sessions/", json={"title": ""})
    assert response.status_code == 422

def test_session_list():
    create_session()
    response = client.get("/sessions/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1

def test_session_get():
    session_id = create_session()
    response = client.get(f"/sessions/{session_id}")
    assert response.status_code == 200
    assert response.json()["id"] == session_id

def test_session_update():
    session_id = create_session()
    response = client.put(f"/sessions/{session_id}", json={"title": "Updated Title"})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"

def test_session_delete():
    session_id = create_session()
    response = client.delete(f"/sessions/{session_id}")
    assert response.status_code == 204

    response = client.get(f"/sessions/{session_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"

def test_message_create_success():
    session_id = create_session()
    response = client.post("/messages/", json={
        "session_id": session_id,
        "role": "user",
        "content": "Hello!"
    })
    assert response.status_code == 201
    assert "id" in response.json()

def test_message_create_failure():
    response = client.post("/messages/", json={
        "session_id": 999999,
        "role": "user",
        "content": "Invalid session"
    })
    assert response.status_code == 404

def test_message_get_all():
    session_id = create_session()
    message_response = client.post("/messages/", json={
        "session_id": session_id,
        "role": "user",
        "content": "Hi from test"
    })
    assert message_response.status_code == 201
    message_id = message_response.json()["id"]

    response = client.get(f"/messages/?session_id={session_id}")
    assert response.status_code == 200
    data = response.json()
    assert any(msg["id"] == message_id for msg in data)
