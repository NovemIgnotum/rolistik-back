import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient
from app.main import app
from app.config import settings
import os
print(f"Database URL: {os.getenv('DATABASE_URL')}")

@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as client:
        yield client

def test_create_user(test_client):
    user_data = {
        "nickname": "testuser",
        "email": "testuser@example.com",
        "hash": "securepassword123!",
        "first_name": "Test",
        "last_name": "User",
    }

    response = test_client.post("/users/create", json=user_data)
    assert response.status_code == 200
