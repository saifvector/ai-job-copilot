"""
Location Matcher Module for Phase 5 AI Job Matching Engine.
Compares candidate preferred locations with job locations across Remote, Hybrid, and Onsite modalities.
"""
import re
from dataclasses import dataclass
from typing import Optional
from core.matching.base import CandidateProfileDTO, JobProfileDTO


@dataclass
class LocationMatchResult:
    score: float
    is_remote: bool
    location_type: str  # "Remote", "Hybrid", "Onsite"


class LocationMatcher:
    """
    Evaluates geographic and workplace modality alignment.
    Supports Remote, Hybrid, and Onsite locations.
    """

    def detect_location_type(self, job: JobProfileDTO) -> str:
        text = f"{job.location} {job.employment_type or ''} {job.title}".lower()
        if "remote" in text or "anywhere" in text or "telecommute" in text or "work from home" in text:
            return "Remote"
        if "hybrid" in text:
            return "Hybrid"
        return "Onsite"

    def match(self, candidate: CandidateProfileDTO, job: JobProfileDTO) -> LocationMatchResult:
        location_type = self.detect_location_type(job)
        is_job_remote = (location_type == "Remote")

        preferred_locations = [
            loc.strip().lower()
            for loc in candidate.preferred_locations
            if loc.strip()
        ]

        # If candidate has no preferred locations specified, default high openness
        if not preferred_locations:
            score = 100.0 if is_job_remote else 85.0
            return LocationMatchResult(score=score, is_remote=is_job_remote, location_type=location_type)

        prefers_remote = any(
            "remote" in loc or "anywhere" in loc or "worldwide" in loc
            for loc in preferred_locations
        )

        job_loc_lower = job.location.lower()

        # Case 1: Job is Remote
        if is_job_remote:
            if prefers_remote:
                score = 100.0
            else:
                # Candidate prefers specific physical locations, but job is Remote
                score = 95.0
            return LocationMatchResult(score=score, is_remote=True, location_type="Remote")

        # Case 2: Job is Physical (Onsite or Hybrid) - check geographic match
        matched_geo = False
        for pref in preferred_locations:
            if pref in ["remote", "anywhere", "worldwide"]:
                continue

            # Substring match for city or country (e.g. "san francisco" in "san francisco, ca")
            pref_tokens = set(re.findall(r"\w+", pref))
            job_tokens = set(re.findall(r"\w+", job_loc_lower))

            if pref_tokens.intersection(job_tokens) or pref in job_loc_lower or job_loc_lower in pref:
                matched_geo = True
                break

        if matched_geo:
            score = 100.0 if location_type == "Onsite" else 95.0
        elif prefers_remote and len(preferred_locations) == 1:
            # Candidate ONLY wants Remote, but job is Onsite/Hybrid in another city
            score = 25.0
        else:
            # Geographic mismatch for onsite/hybrid position
            score = 40.0

        return LocationMatchResult(
            score=round(score, 1),
            is_remote=is_job_remote,
            location_type=location_type,
        )
