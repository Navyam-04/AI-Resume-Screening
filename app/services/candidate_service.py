from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.candidate import Candidate
from app.schemas.candidate import CandidateCreate


class DuplicateCandidateError(Exception):
    """Raised when a candidate with the same email already exists."""
    pass


def create_candidate_record(
    db: Session,
    data: CandidateCreate
) -> Candidate:
    """
    Create and save a new candidate in the database.
    """

    new_candidate = Candidate(
        full_name=data.full_name,
        email=data.email,
        experience_years=data.experience_years,
        skills=data.skills,
    )

    db.add(new_candidate)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise DuplicateCandidateError(
            f"A candidate with email '{data.email}' already exists."
        )

    db.refresh(new_candidate)

    return new_candidate