from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.candidate import Candidate
from app.schemas.candidate import CandidateCreate, CandidateResponse

router = APIRouter()


@router.post("/candidates", response_model=CandidateResponse, status_code=201)
def create_candidate(
    candidate: CandidateCreate,
    db: Session = Depends(get_db),
):
    new_candidate = Candidate(
        full_name=candidate.full_name,
        email=candidate.email,
        experience_years=candidate.experience_years,
        skills=candidate.skills,
    )

    db.add(new_candidate)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="A candidate with this email already exists",
        )

    db.refresh(new_candidate)

    return new_candidate


@router.get("/candidates", response_model=List[CandidateResponse])
def list_candidates(
    db: Session = Depends(get_db),
):
    return db.query(Candidate).all()


@router.get("/candidates/{candidate_id}", response_model=CandidateResponse)
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db),
):
    candidate = (
        db.query(Candidate)
        .filter(Candidate.id == candidate_id)
        .first()
    )

    if candidate is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found",
        )

    return candidate