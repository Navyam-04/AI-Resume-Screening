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


def test_list_candidates():
    payload = {
        "full_name": "List Test Candidate",
        "email": "listtest@example.com",
        "experience_years": 1,
        "skills": ["SQL"]
    }
    client.post("/api/v1/candidates", json=payload)

    response = client.get("/api/v1/candidates")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


def test_get_candidate_by_id():
    payload = {
        "full_name": "Fetch Me",
        "email": "fetchme@example.com",
        "experience_years": 2,
        "skills": ["Go"]
    }
    create_response = client.post("/api/v1/candidates", json=payload)
    candidate_id = create_response.json()["id"]

    response = client.get(f"/api/v1/candidates/{candidate_id}")

    assert response.status_code == 200
    assert response.json()["id"] == candidate_id
    assert response.json()["full_name"] == "Fetch Me"


def test_get_candidate_not_found():
    response = client.get("/api/v1/candidates/999999")

    assert response.status_code == 404