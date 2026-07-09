import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.schemas.resume import ResumeUploadResponse
from app.schemas.extraction import ExtractedResumeData
from app.schemas.candidate import CandidateCreate, CandidateResponse

from app.services.resume_parser import get_parser
from app.services.ai_extractor import extract_candidate_info
from app.services.candidate_service import (
    create_candidate_record,
    DuplicateCandidateError,
)

router = APIRouter()

UPLOAD_DIR = "uploads"


async def _save_and_parse(file: UploadFile) -> tuple[str, str]:
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in (".pdf", ".docx"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported",
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    saved_filename = f"{uuid.uuid4().hex}{ext}"
    saved_path = os.path.join(UPLOAD_DIR, saved_filename)

    contents = await file.read()

    with open(saved_path, "wb") as f:
        f.write(contents)

    try:
        parser = get_parser(file.filename)
        extracted_text = parser.extract_text(saved_path)
    except Exception:
        raise HTTPException(
            status_code=422,
            detail="Could not read this file - it may be corrupted",
        )

    return saved_filename, extracted_text


@router.post(
    "/resumes/upload",
    response_model=ResumeUploadResponse,
    status_code=201,
)
async def upload_resume(file: UploadFile = File(...)):
    saved_filename, extracted_text = await _save_and_parse(file)

    return ResumeUploadResponse(
        original_filename=file.filename,
        saved_as=saved_filename,
        extracted_text=extracted_text,
    )


@router.post(
    "/resumes/extract",
    response_model=ExtractedResumeData,
)
async def extract_resume(file: UploadFile = File(...)):
    _, extracted_text = await _save_and_parse(file)

    try:
        return extract_candidate_info(extracted_text)

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="AI extraction failed - check your Gemini API key and quota",
        )


@router.post(
    "/resumes/upload-and-create",
    response_model=CandidateResponse,
    status_code=201,
)
async def upload_and_create_candidate(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    _, extracted_text = await _save_and_parse(file)

    try:
        extracted = extract_candidate_info(extracted_text)

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="AI extraction failed - check your Gemini API key and quota",
        )

    try:
        candidate_data = CandidateCreate(
            full_name=extracted.full_name,
            email=extracted.email,
            experience_years=extracted.experience_years,
            skills=extracted.skills,
        )

    except ValidationError as e:
        missing_fields = ", ".join(
            str(err["loc"][0])
            for err in e.errors()
        )

        raise HTTPException(
            status_code=422,
            detail=(
                f"Resume extraction was incomplete or invalid for: "
                f"{missing_fields}. "
                "Review the extraction using "
                "POST /resumes/extract first."
            ),
        )

    try:
        return create_candidate_record(
            db,
            candidate_data,
        )

    except DuplicateCandidateError:
        raise HTTPException(
            status_code=400,
            detail="A candidate with this email already exists",
        )