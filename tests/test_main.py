import pytest
from fastapi.testclient import TestClient
import sys
import os

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from main import app


client = TestClient(app)


def test_swagger_ui():
    response = client.get("/swagger")
    assert response.status_code == 200
    assert "Swagger UI" in response.text


def test_redoc_ui():
    response = client.get("/redoc")
    assert response.status_code == 200
    assert "ReDoc" in response.text


def test_root():
    response = client.get("/")
    print(response.json())
    assert response.status_code == 200
    assert response.json() == {"message": "API is running"}


def test_not_found():
    response = client.get("/nonexistent")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


def test_api_v1_endpoint():
    payload = {
        "name": "Test Item",
        "description": "A test description",
        "price": 19.99,
        "tax": 2.99
    }
    
    response = client.post("/api/v1/items/", json=payload)
    
    assert response.status_code == 200
    assert response.json() == {"item": payload}


def test_login():
    response = client.post("/api/v1/login", json={
        "username": "user1",
        "password": "password1",
        "email": "user1@example.com"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_access_protected_route():
    response = client.post("/api/v1/login", json={"username": "user1", "password": "password1"})
    token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    protected_response = client.get("/users/me", headers=headers)
    assert protected_response.status_code == 200
