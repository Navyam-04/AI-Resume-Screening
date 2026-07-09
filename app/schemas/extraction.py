from typing import List, Optional

from pydantic import BaseModel, Field


class ExtractedResumeData(BaseModel):
    full_name: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)
    experience_years: Optional[int] = Field(default=None)
    skills: List[str] = Field(default_factory=list)