from fastapi.testclient import TestClient

from app.main import app
from app.database.session import SessionLocal
from app.models.job import Job

client = TestClient(app)


def _cleanup(job_id: int):
    db = SessionLocal()
    db.query(Job).filter(Job.id == job_id).delete()
    db.commit()
    db.close()


def test_create_job_success():
    payload = {
        "title": "Backend Engineer",
        "description": "We are looking for a backend engineer with FastAPI experience.",
        "required_skills": ["Python", "FastAPI", "PostgreSQL"],
        "min_experience_years": 2,
    }

    response = client.post("/api/v1/jobs", json=payload)

    assert response.status_code == 201
    data = response.json()

    assert data["title"] == payload["title"]
    assert data["required_skills"] == payload["required_skills"]

    _cleanup(data["id"])


def test_create_job_missing_skills():
    payload = {
        "title": "Backend Engineer",
        "description": "We are looking for a backend engineer with FastAPI experience.",
        "required_skills": [],
        "min_experience_years": 2,
    }

    response = client.post("/api/v1/jobs", json=payload)

    assert response.status_code == 422


def test_list_jobs():
    payload = {
        "title": "Data Engineer",
        "description": "Looking for someone comfortable with data pipelines.",
        "required_skills": ["Python", "SQL"],
        "min_experience_years": 1,
    }

    created = client.post("/api/v1/jobs", json=payload)
    assert created.status_code == 201

    response = client.get("/api/v1/jobs")

    assert response.status_code == 200
    assert len(response.json()) >= 1

    _cleanup(created.json()["id"])


def test_get_job_by_id():
    payload = {
        "title": "ML Engineer",
        "description": "Ranking models and feature engineering for candidate scoring.",
        "required_skills": ["Python", "scikit-learn"],
        "min_experience_years": 3,
    }

    created = client.post("/api/v1/jobs", json=payload)
    assert created.status_code == 201

    job_id = created.json()["id"]

    response = client.get(f"/api/v1/jobs/{job_id}")

    assert response.status_code == 200
    assert response.json()["id"] == job_id
    assert response.json()["title"] == payload["title"]

    _cleanup(job_id)


def test_get_job_not_found():
    response = client.get("/api/v1/jobs/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"