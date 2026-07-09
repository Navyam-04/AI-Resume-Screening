import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.resume_parser import get_parser
from app.schemas.resume import ResumeUploadResponse

router = APIRouter()
UPLOAD_DIR = "uploads"


@router.post("/resumes/upload", response_model=ResumeUploadResponse, status_code=201)
async def upload_resume(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".pdf", ".docx"):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Random filename on disk - never trust the client's filename for
    # storage (collisions, weird characters, path traversal risk).
    saved_filename = f"{uuid.uuid4().hex}{ext}"
    saved_path = os.path.join(UPLOAD_DIR, saved_filename)

    contents = await file.read()
    with open(saved_path, "wb") as f:
        f.write(contents)

    try:
        parser = get_parser(file.filename)
        extracted_text = parser.extract_text(saved_path)
    except Exception:
        raise HTTPException(status_code=422, detail="Could not read this file - it may be corrupted")

    return ResumeUploadResponse(
        original_filename=file.filename,
        saved_as=saved_filename,
        extracted_text=extracted_text,
    )