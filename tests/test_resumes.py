import uuid
from unittest.mock import patch

import fitz
from docx import Document
from fastapi.testclient import TestClient

from app.database.session import SessionLocal
from app.main import app
from app.models.candidate import Candidate
from app.schemas.extraction import ExtractedResumeData

client = TestClient(app)


def _make_pdf(path, text):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    doc.save(path)
    doc.close()


def _make_docx(path, text):
    doc = Document()
    doc.add_paragraph(text)
    doc.save(path)


def _cleanup(email: str):
    db = SessionLocal()
    db.query(Candidate).filter(
        Candidate.email == email
    ).delete()
    db.commit()
    db.close()


def test_upload_pdf_resume(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    _make_pdf(str(pdf_path), "John Doe - Python Developer")

    with open(pdf_path, "rb") as f:
        response = client.post(
            "/api/v1/resumes/upload",
            files={"file": ("sample.pdf", f, "application/pdf")},
        )

    assert response.status_code == 201
    assert "John Doe" in response.json()["extracted_text"]


def test_upload_docx_resume(tmp_path):
    docx_path = tmp_path / "sample.docx"
    _make_docx(str(docx_path), "Jane Smith - Backend Engineer")

    with open(docx_path, "rb") as f:
        response = client.post(
            "/api/v1/resumes/upload",
            files={
                "file": (
                    "sample.docx",
                    f,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

    assert response.status_code == 201
    assert "Jane Smith" in response.json()["extracted_text"]


def test_upload_unsupported_file_type(tmp_path):
    txt_path = tmp_path / "sample.txt"
    txt_path.write_text("Just some text")

    with open(txt_path, "rb") as f:
        response = client.post(
            "/api/v1/resumes/upload",
            files={"file": ("sample.txt", f, "text/plain")},
        )

    assert response.status_code == 400


@patch("app.api.v1.endpoints.resumes.extract_candidate_info")
def test_extract_resume_endpoint(mock_extract, tmp_path):
    mock_extract.return_value = ExtractedResumeData(
        full_name="Jane Smith",
        email="jane@example.com",
        experience_years=4,
        skills=["Python", "FastAPI"],
    )

    docx_path = tmp_path / "sample.docx"
    _make_docx(
        str(docx_path),
        "Jane Smith - Backend Engineer, 4 years experience",
    )

    with open(docx_path, "rb") as f:
        response = client.post(
            "/api/v1/resumes/extract",
            files={
                "file": (
                    "sample.docx",
                    f,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

    assert response.status_code == 200
    assert response.json()["full_name"] == "Jane Smith"
    mock_extract.assert_called_once()


@patch("app.api.v1.endpoints.resumes.extract_candidate_info")
def test_upload_and_create_candidate_success(mock_extract, tmp_path):
    email = f"pipeline-{uuid.uuid4().hex[:8]}@example.com"

    mock_extract.return_value = ExtractedResumeData(
        full_name="Pipeline Candidate",
        email=email,
        experience_years=5,
        skills=["Python", "SQL"],
    )

    docx_path = tmp_path / "sample.docx"
    _make_docx(str(docx_path), "Pipeline Candidate - 5 years experience")

    with open(docx_path, "rb") as f:
        response = client.post(
            "/api/v1/resumes/upload-and-create",
            files={
                "file": (
                    "sample.docx",
                    f,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

    assert response.status_code == 201

    data = response.json()

    get_response = client.get(f"/api/v1/candidates/{data['id']}")

    assert get_response.status_code == 200

    _cleanup(email)


@patch("app.api.v1.endpoints.resumes.extract_candidate_info")
def test_upload_and_create_candidate_incomplete_extraction(
    mock_extract,
    tmp_path,
):
    mock_extract.return_value = ExtractedResumeData(
        full_name="Incomplete Candidate",
        email=None,
        experience_years=None,
        skills=[],
    )

    docx_path = tmp_path / "sample.docx"
    _make_docx(str(docx_path), "Incomplete Candidate")

    with open(docx_path, "rb") as f:
        response = client.post(
            "/api/v1/resumes/upload-and-create",
            files={
                "file": (
                    "sample.docx",
                    f,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

    assert response.status_code == 422
    assert "email" in response.json()["detail"]


@patch("app.api.v1.endpoints.resumes.extract_candidate_info")
def test_upload_and_create_candidate_duplicate_email(
    mock_extract,
    tmp_path,
):
    email = f"dup-pipeline-{uuid.uuid4().hex[:8]}@example.com"

    mock_extract.return_value = ExtractedResumeData(
        full_name="Dup Pipeline",
        email=email,
        experience_years=2,
        skills=["Java"],
    )

    docx_path = tmp_path / "sample.docx"
    _make_docx(str(docx_path), "Dup Pipeline")

    with open(docx_path, "rb") as f:
        first = client.post(
            "/api/v1/resumes/upload-and-create",
            files={
                "file": (
                    "sample.docx",
                    f,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

    assert first.status_code == 201

    with open(docx_path, "rb") as f:
        second = client.post(
            "/api/v1/resumes/upload-and-create",
            files={
                "file": (
                    "sample.docx",
                    f,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

    assert second.status_code == 400

    _cleanup(email)