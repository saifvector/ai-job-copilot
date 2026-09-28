"""
Skill Matcher Module for Phase 5 AI Job Matching Engine.
Compares user candidate skills against job requirements using semantic similarity.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from core.matching.base import CandidateProfileDTO, JobProfileDTO
from core.matching.semantic import SemanticMatcher, default_semantic_matcher


@dataclass
class SkillMatchResult:
    score: float
    matched_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)


class SkillMatcher:
    """
    Evaluates alignment between Candidate competencies and Job technical requirements.
    Produces matched skills, missing skills, and a normalized [0.0, 100.0] score.
    """

    def __init__(self, semantic_matcher: Optional[SemanticMatcher] = None):
        self.semantic_matcher = semantic_matcher or default_semantic_matcher

    def match(self, candidate: CandidateProfileDTO, job: JobProfileDTO) -> SkillMatchResult:
        # Collect candidate's universe of skills
        candidate_skills: Set[str] = {s.strip() for s in candidate.skills if s.strip()}

        # Augment with technologies mentioned in candidate projects
        for proj in candidate.projects:
            for tech in proj.get("technologies", []):
                if tech and isinstance(tech, str):
                    candidate_skills.add(tech.strip())

        # Target job skills
        job_skills: List[str] = [s.strip() for s in job.skills if s.strip()]

        # If job has no tagged skills, fallback to scanning description for tech tokens
        if not job_skills:
            job_text = f"{job.title} {job.description} {job.requirements or ''}".lower()
            # If candidate skills appear in job text, treat those as matched
            found_skills = [
                s for s in candidate_skills
                if len(s) > 2 and s.lower() in job_text
            ]
            if found_skills:
                # Moderate default score if job didn't specify strict skill list
                score = min(90.0, 50.0 + len(found_skills) * 8.0)
                return SkillMatchResult(
                    score=round(score, 1),
                    matched_skills=sorted(found_skills),
                    missing_skills=[],
                )
            return SkillMatchResult(score=60.0, matched_skills=[], missing_skills=[])

        matched: List[str] = []
        missing: List[str] = []
        candidate_skill_list = list(candidate_skills)

        for j_skill in job_skills:
            best_match, sim = self.semantic_matcher.find_best_match(
                query=j_skill,
                candidates=candidate_skill_list,
                threshold=0.80,
            )
            if best_match:
                matched.append(j_skill)
            else:
                missing.append(j_skill)

        total_req = len(job_skills)
        if total_req == 0:
            score = 70.0
        else:
            base_score = (len(matched) / total_req) * 100.0
            # Slight bonus (up to 5 points) if user has additional high confidence skills
            bonus = min(5.0, len(candidate_skills) * 0.2) if len(matched) > 0 else 0.0
            score = min(100.0, base_score + bonus)

        return SkillMatchResult(
            score=round(score, 1),
            matched_skills=sorted(list(set(matched))),
            missing_skills=sorted(list(set(missing))),
        )
