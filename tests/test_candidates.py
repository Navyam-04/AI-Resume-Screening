import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal
from app.models.candidate import Candidate

client = TestClient(app)


def _unique_email():
    return f"test-{uuid.uuid4().hex[:8]}@example.com"


def _cleanup(email: str):
    db = SessionLocal()
    db.query(Candidate).filter(Candidate.email == email).delete()
    db.commit()
    db.close()


def test_create_candidate_success():
    email = _unique_email()
    payload = {"full_name": "Asha Rao", "email": email, "experience_years": 3, "skills": ["Python", "FastAPI"]}
    response = client.post("/api/v1/candidates", json=payload)
    assert response.status_code == 201
    assert response.json()["email"] == email
    _cleanup(email)


def test_create_candidate_duplicate_email():
    email = _unique_email()
    payload = {"full_name": "Dup Test", "email": email, "experience_years": 1, "skills": ["Java"]}
    assert client.post("/api/v1/candidates", json=payload).status_code == 201
    assert client.post("/api/v1/candidates", json=payload).status_code == 400
    _cleanup(email)


def test_create_candidate_invalid_email():
    payload = {"full_name": "Bad Email Candidate", "email": "not-an-email", "experience_years": 2, "skills": ["Java"]}
    assert client.post("/api/v1/candidates", json=payload).status_code == 422


def test_create_candidate_negative_experience():
    payload = {"full_name": "Negative Years", "email": _unique_email(), "experience_years": -1, "skills": ["Java"]}
    assert client.post("/api/v1/candidates", json=payload).status_code == 422


def test_list_candidates():
    email = _unique_email()
    client.post("/api/v1/candidates", json={"full_name": "List Test Candidate", "email": email, "experience_years": 1, "skills": ["SQL"]})
    response = client.get("/api/v1/candidates")
    assert response.status_code == 200
    assert len(response.json()) >= 1
    _cleanup(email)


def test_get_candidate_by_id():
    email = _unique_email()
    created = client.post("/api/v1/candidates", json={"full_name": "Fetch Me", "email": email, "experience_years": 2, "skills": ["Go"]})
    candidate_id = created.json()["id"]
    response = client.get(f"/api/v1/candidates/{candidate_id}")
    assert response.status_code == 200
    assert response.json()["full_name"] == "Fetch Me"
    _cleanup(email)


def test_get_candidate_not_found():
    assert client.get("/api/v1/candidates/999999").status_code == 404