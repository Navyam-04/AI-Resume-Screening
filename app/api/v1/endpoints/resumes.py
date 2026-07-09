import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.resume_parser import get_parser
from app.services.ai_extractor import extract_candidate_info
from app.schemas.resume import ResumeUploadResponse
from app.schemas.extraction import ExtractedResumeData

router = APIRouter()
UPLOAD_DIR = "uploads"


async def _save_and_parse(file: UploadFile) -> tuple[str, str]:
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".pdf", ".docx"):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    saved_filename = f"{uuid.uuid4().hex}{ext}"
    saved_path = os.path.join(UPLOAD_DIR, saved_filename)

    contents = await file.read()
    with open(saved_path, "wb") as f:
        f.write(contents)

    try:
        parser = get_parser(file.filename)
        text = parser.extract_text(saved_path)
    except Exception:
        raise HTTPException(status_code=422, detail="Could not read this file - it may be corrupted")

    return saved_filename, text


@router.post("/resumes/upload", response_model=ResumeUploadResponse, status_code=201)
async def upload_resume(file: UploadFile = File(...)):
    saved_filename, text = await _save_and_parse(file)
    return ResumeUploadResponse(original_filename=file.filename, saved_as=saved_filename, extracted_text=text)


@router.post("/resumes/extract", response_model=ExtractedResumeData, status_code=200)
async def extract_resume(file: UploadFile = File(...)):
    _, text = await _save_and_parse(file)
    try:
        return extract_candidate_info(text)
    except Exception:
        raise HTTPException(status_code=502, detail="AI extraction failed - check your Gemini API key and quota")