from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_candidate_success():
    payload = {
        "full_name": "Asha Rao",
        "email": "asha.rao@example.com",
        "experience_years": 3,
        "skills": ["Python", "FastAPI"]
    }
    response = client.post("/api/v1/candidates", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["full_name"] == "Asha Rao"


def test_create_candidate_invalid_email():
    payload = {
        "full_name": "Bad Email Candidate",
        "email": "not-an-email",
        "experience_years": 2,
        "skills": ["Java"]
    }
    response = client.post("/api/v1/candidates", json=payload)
    assert response.status_code == 422


def test_create_candidate_negative_experience():
    payload = {
        "full_name": "Negative Years",
        "email": "neg@example.com",
        "experience_years": -1,
        "skills": ["Java"]
    }
    response = client.post("/api/v1/candidates", json=payload)
    assert response.status_code == 422