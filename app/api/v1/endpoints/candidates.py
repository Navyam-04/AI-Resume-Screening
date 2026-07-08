from fastapi import APIRouter
from app.schemas.candidate import CandidateCreate, CandidateResponse

router = APIRouter()

# TEMPORARY in-memory storage — replaced by PostgreSQL later.
# Just proves the schema + endpoint work end-to-end for now.
candidates_db = []
next_id = 1


@router.post("/candidates", response_model=CandidateResponse, status_code=201)
def create_candidate(candidate: CandidateCreate):
    global next_id

    new_candidate = CandidateResponse(
        id=next_id,
        full_name=candidate.full_name,
        email=candidate.email,
        experience_years=candidate.experience_years,
        skills=candidate.skills,
    )

    candidates_db.append(new_candidate)
    next_id += 1

    return new_candidate