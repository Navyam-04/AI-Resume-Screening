from typing import List

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CandidateCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    experience_years: int = Field(..., ge=0, le=50)
    skills: List[str] = Field(..., min_length=1)


class CandidateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    experience_years: int
    skills: List[str]