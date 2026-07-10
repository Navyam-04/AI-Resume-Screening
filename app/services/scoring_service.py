import heapq
from typing import List

from app.models.candidate import Candidate
from app.models.job import Job
from app.schemas.scoring import CandidateScore


def score_candidate_against_job(
    candidate: Candidate,
    job: Job,
) -> CandidateScore:

    candidate_skills = {
        skill.lower().strip()
        for skill in candidate.skills
    }

    required_skills = {
        skill.lower().strip()
        for skill in job.required_skills
    }

    matched_skills = candidate_skills & required_skills
    missing_skills = required_skills - candidate_skills

    if required_skills:
        skill_match_percentage = (
            len(matched_skills) / len(required_skills)
        ) * 100
    else:
        skill_match_percentage = 0

    experience_met = (
        candidate.experience_years >=
        job.min_experience_years
    )

    overall_score = (
        skill_match_percentage * 0.7
    ) + (
        30 if experience_met else 0
    )

    return CandidateScore(
        candidate_id=candidate.id,
        candidate_name=candidate.full_name,
        overall_score=round(overall_score, 2),
        skill_match_percentage=round(
            skill_match_percentage,
            2,
        ),
        matched_skills=sorted(matched_skills),
        missing_skills=sorted(missing_skills),
        experience_met=experience_met,
    )


def rank_candidates_for_job(
    job: Job,
    candidates: List[Candidate],
    top_k: int = 10,
) -> List[CandidateScore]:

    scores = [
        score_candidate_against_job(candidate, job)
        for candidate in candidates
    ]

    return heapq.nlargest(
        top_k,
        scores,
        key=lambda score: score.overall_score,
    )