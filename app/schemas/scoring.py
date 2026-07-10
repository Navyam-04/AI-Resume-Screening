from pydantic import BaseModel
from typing import List


class CandidateScore(BaseModel):
    candidate_id: int
    candidate_name: str
    overall_score: float
    skill_match_percentage: float
    matched_skills: List[str]
    missing_skills: List[str]
    experience_met: bool


class RankedCandidatesResponse(BaseModel):
    job_id: int
    job_title: str
    ranked_candidates: List[CandidateScore]