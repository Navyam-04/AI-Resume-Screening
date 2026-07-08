from pydantic import BaseModel, EmailStr, Field
from typing import List


class CandidateCreate(BaseModel):
    """What the CLIENT sends us. REQUEST model."""
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    experience_years: int = Field(..., ge=0, le=50)
    skills: List[str] = Field(..., min_length=1)


class CandidateResponse(BaseModel):
    """What WE send back. RESPONSE model.
    Has 'id' — client never sends this, we generate it.
    That's why request/response are two separate models."""
    id: int
    full_name: str
    email: EmailStr
    experience_years: int
    skills: List[str]