import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root_online():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API online"}
    
def test_read_root_offline():
    response = client.get("/dontfound")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}