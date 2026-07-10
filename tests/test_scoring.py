import uuid

from fastapi.testclient import TestClient

from app.main import app
from app.database.session import SessionLocal
from app.models.candidate import Candidate
from app.models.job import Job

client = TestClient(app)


def _cleanup_candidate(email: str):
    db = SessionLocal()
    db.query(Candidate).filter(Candidate.email == email).delete()
    db.commit()
    db.close()


def _cleanup_job(job_id: int):
    db = SessionLocal()
    db.query(Job).filter(Job.id == job_id).delete()
    db.commit()
    db.close()


def _make_candidate(skills, experience_years):
    email = f"{uuid.uuid4().hex[:8]}@example.com"

    payload = {
        "full_name": "Test Candidate",
        "email": email,
        "experience_years": experience_years,
        "skills": skills,
    }

    response = client.post("/api/v1/candidates", json=payload)

    return response.json(), email


def _make_job():
    payload = {
        "title": "Backend Engineer",
        "description": "Need FastAPI and PostgreSQL experience.",
        "required_skills": [
            "Python",
            "FastAPI",
            "PostgreSQL",
        ],
        "min_experience_years": 3,
    }

    response = client.post("/api/v1/jobs", json=payload)

    return response.json()


def test_score_single_candidate():
    job = _make_job()

    candidate, email = _make_candidate(
        ["Python", "FastAPI", "PostgreSQL"],
        5,
    )

    response = client.get(
        f"/api/v1/jobs/{job['id']}/candidates/{candidate['id']}/score"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["experience_met"] is True
    assert data["overall_score"] == 100.0

    _cleanup_candidate(email)
    _cleanup_job(job["id"])


def test_ranked_candidates_orders_by_score():
    job = _make_job()

    strong, email1 = _make_candidate(
        ["Python", "FastAPI", "PostgreSQL"],
        5,
    )

    medium, email2 = _make_candidate(
        ["Python", "FastAPI"],
        4,
    )

    weak, email3 = _make_candidate(
        ["Python"],
        1,
    )

    response = client.get(
        f"/api/v1/jobs/{job['id']}/ranked-candidates",
        params={"top_k": 2},
    )

    assert response.status_code == 200

    ranked = response.json()["ranked_candidates"]

    assert len(ranked) == 2

    assert ranked[0]["candidate_id"] == strong["id"]

    assert ranked[0]["overall_score"] >= ranked[1]["overall_score"]

    _cleanup_candidate(email1)
    _cleanup_candidate(email2)
    _cleanup_candidate(email3)
    _cleanup_job(job["id"])


def test_score_job_not_found():
    candidate, email = _make_candidate(
        ["Python"],
        2,
    )

    response = client.get(
        f"/api/v1/jobs/999999/candidates/{candidate['id']}/score"
    )

    assert response.status_code == 404

    _cleanup_candidate(email)


def test_score_candidate_not_found():
    job = _make_job()

    response = client.get(
        f"/api/v1/jobs/{job['id']}/candidates/999999/score"
    )

    assert response.status_code == 404

    _cleanup_job(job["id"])