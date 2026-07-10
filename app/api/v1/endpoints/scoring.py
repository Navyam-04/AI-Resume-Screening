from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.candidate import Candidate
from app.models.job import Job
from app.schemas.scoring import (
    CandidateScore,
    RankedCandidatesResponse,
)
from app.services.scoring_service import (
    score_candidate_against_job,
    rank_candidates_for_job,
)

router = APIRouter()


@router.get(
    "/jobs/{job_id}/candidates/{candidate_id}/score",
    response_model=CandidateScore,
)
def score_one_candidate(
    job_id: int,
    candidate_id: int,
    db: Session = Depends(get_db),
):
    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

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

    return score_candidate_against_job(
        candidate,
        job,
    )


@router.get(
    "/jobs/{job_id}/ranked-candidates",
    response_model=RankedCandidatesResponse,
)
def ranked_candidates(
    job_id: int,
    top_k: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
):
    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    candidates = db.query(Candidate).all()

    ranked = rank_candidates_for_job(
        job,
        candidates,
        top_k=top_k,
    )

    return RankedCandidatesResponse(
        job_id=job.id,
        job_title=job.title,
        ranked_candidates=ranked,
    )