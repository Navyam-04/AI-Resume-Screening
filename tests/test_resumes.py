import fitz
from docx import Document
from fastapi.testclient import TestClient

from app.main import app

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