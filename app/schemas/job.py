from pydantic import BaseModel, Field, ConfigDict
from typing import List


class JobCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=150)
    description: str = Field(..., min_length=10)
    required_skills: List[str] = Field(..., min_length=1)
    min_experience_years: int = Field(default=0, ge=0, le=50)


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    required_skills: List[str]
    min_experience_years: int