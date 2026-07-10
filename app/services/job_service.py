from sqlalchemy.orm import Session
from app.models.job import Job
from app.schemas.job import JobCreate


def create_job_record(db: Session, data: JobCreate) -> Job:
    new_job = Job(
        title=data.title,
        description=data.description,
        required_skills=data.required_skills,
        min_experience_years=data.min_experience_years,
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job