"""
Unit tests for Phase 5 Matching Engine individual Matcher modules:
- SemanticMatcher (synonyms, acronyms: ML <-> Machine Learning, AI <-> Artificial Intelligence)
- SkillMatcher
- ExperienceMatcher
- RoleMatcher
- LocationMatcher
- EducationMatcher
"""
import uuid
import pytest
from core.matching.base import CandidateProfileDTO, JobProfileDTO
from core.matching.education_matcher import EducationMatcher
from core.matching.experience_matcher import ExperienceMatcher
from core.matching.location_matcher import LocationMatcher
from core.matching.role_matcher import RoleMatcher
from core.matching.semantic import FastSemanticProvider, SemanticMatcher
from core.matching.skill_matcher import SkillMatcher


@pytest.fixture
def semantic_matcher():
    return SemanticMatcher(provider=FastSemanticProvider())


@pytest.fixture
def sample_candidate():
    return CandidateProfileDTO(
        user_id=uuid.uuid4(),
        preferred_roles=["AI Engineer", "Machine Learning Engineer"],
        preferred_locations=["Remote", "San Francisco"],
        years_of_experience=4,
        skills=["Python", "FastAPI", "PostgreSQL", "Machine Learning", "PyTorch"],
        educations=[
            {
                "degree": "B.Tech",
                "field_of_study": "Computer Science and AI",
                "institution": "Tech University",
            }
        ],
        experiences=[
            {
                "role": "Machine Learning Engineer",
                "company": "AI Labs",
                "description": "Built LLM inference pipelines with FastAPI and PyTorch.",
            }
        ],
        projects=[
            {
                "title": "Autonomous Agent",
                "description": "Built multi-agent framework.",
                "technologies": ["Python", "FastAPI", "Docker"],
            }
        ],
    )


class TestSemanticMatcher:
    def test_exact_match(self, semantic_matcher):
        is_match, score = semantic_matcher.is_match("Python", "python")
        assert is_match is True
        assert score == 1.0

    def test_ml_matches_machine_learning(self, semantic_matcher):
        """User requirement: 'Machine Learning' matches 'ML'"""
        is_match, score = semantic_matcher.is_match("Machine Learning", "ML")
        assert is_match is True
        assert score >= 0.90

    def test_ai_matches_artificial_intelligence(self, semantic_matcher):
        """User requirement: 'Artificial Intelligence' matches 'AI'"""
        is_match, score = semantic_matcher.is_match("Artificial Intelligence", "AI")
        assert is_match is True
        assert score >= 0.90

    def test_tech_synonyms(self, semantic_matcher):
        assert semantic_matcher.is_match("K8s", "Kubernetes")[0] is True
        assert semantic_matcher.is_match("Postgres", "PostgreSQL")[0] is True
        assert semantic_matcher.is_match("JS", "JavaScript")[0] is True
        assert semantic_matcher.is_match("TS", "TypeScript")[0] is True
        assert semantic_matcher.is_match("GCP", "Google Cloud")[0] is True

    def test_find_best_match(self, semantic_matcher):
        candidates = ["Docker", "Kubernetes", "Machine Learning", "React"]
        match, score = semantic_matcher.find_best_match("ML", candidates)
        assert match == "Machine Learning"
        assert score >= 0.90


class TestSkillMatcher:
    def test_matched_and_missing_skills(self, semantic_matcher, sample_candidate):
        matcher = SkillMatcher(semantic_matcher=semantic_matcher)
        job = JobProfileDTO(
            id=uuid.uuid4(),
            title="Senior AI Engineer",
            company="Neural Corp",
            location="Remote",
            skills=["Python", "FastAPI", "Docker", "AWS"],
        )

        result = matcher.match(sample_candidate, job)

        # Python and FastAPI are in candidate skills, Docker is in candidate projects!
        assert "Python" in result.matched_skills
        assert "FastAPI" in result.matched_skills
        assert "Docker" in result.matched_skills
        assert "AWS" in result.missing_skills
        # 3 out of 4 matched
        assert result.score >= 75.0

    def test_job_with_no_skills_fallback(self, semantic_matcher, sample_candidate):
        matcher = SkillMatcher(semantic_matcher=semantic_matcher)
        job = JobProfileDTO(
            id=uuid.uuid4(),
            title="Python Developer",
            company="Tech Corp",
            location="Remote",
            description="Looking for an experienced engineer with Python and PostgreSQL knowledge.",
            skills=[],
        )

        result = matcher.match(sample_candidate, job)
        assert result.score >= 50.0
        assert "Python" in result.matched_skills or "PostgreSQL" in result.matched_skills


class TestExperienceMatcher:
    def test_experience_years_sufficient(self, sample_candidate):
        matcher = ExperienceMatcher()
        job = JobProfileDTO(
            id=uuid.uuid4(),
            title="Mid-level AI Engineer",
            company="Tech Corp",
            location="Remote",
            description="Requires 3+ years of experience in AI/ML software development.",
        )

        result = matcher.match(sample_candidate, job)
        assert result.candidate_years == 4
        assert result.required_years == 3
        assert result.score >= 90.0

    def test_experience_years_insufficient(self, sample_candidate):
        matcher = ExperienceMatcher()
        job = JobProfileDTO(
            id=uuid.uuid4(),
            title="Staff Principal AI Architect",
            company="Tech Corp",
            location="Remote",
            description="Requires 8+ years of industry experience.",
        )

        result = matcher.match(sample_candidate, job)
        assert result.required_years >= 7
        assert result.score < 80.0


class TestRoleMatcher:
    def test_role_alignment_direct(self, semantic_matcher, sample_candidate):
        matcher = RoleMatcher(semantic_matcher=semantic_matcher)
        job = JobProfileDTO(
            id=uuid.uuid4(),
            title="Senior Machine Learning Engineer",
            company="AI Labs",
            location="Remote",
        )

        result = matcher.match(sample_candidate, job)
        assert result.score >= 85.0
        assert result.matched_role in sample_candidate.preferred_roles

    def test_role_alignment_dissimilar(self, semantic_matcher, sample_candidate):
        matcher = RoleMatcher(semantic_matcher=semantic_matcher)
        job = JobProfileDTO(
            id=uuid.uuid4(),
            title="Senior Accounting Specialist",
            company="Finance Corp",
            location="Remote",
        )

        result = matcher.match(sample_candidate, job)
        assert result.score <= 35.0


class TestLocationMatcher:
    def test_remote_job_with_remote_candidate(self, sample_candidate):
        matcher = LocationMatcher()
        job = JobProfileDTO(
            id=uuid.uuid4(),
            title="Backend Engineer",
            company="Remote First Inc",
            location="Remote",
        )

        result = matcher.match(sample_candidate, job)
        assert result.score == 100.0
        assert result.is_remote is True
        assert result.location_type == "Remote"

    def test_physical_location_match(self, sample_candidate):
        matcher = LocationMatcher()
        job = JobProfileDTO(
            id=uuid.uuid4(),
            title="ML Engineer",
            company="SF Labs",
            location="San Francisco, CA",
        )

        result = matcher.match(sample_candidate, job)
        assert result.score >= 95.0

    def test_location_mismatch_onsite(self, sample_candidate):
        matcher = LocationMatcher()
        job = JobProfileDTO(
            id=uuid.uuid4(),
            title="Systems Engineer",
            company="Munich Systems",
            location="Munich, Germany",
        )

        result = matcher.match(sample_candidate, job)
        assert result.score <= 45.0


class TestEducationMatcher:
    def test_btech_cs_education(self, sample_candidate):
        matcher = EducationMatcher()
        job = JobProfileDTO(
            id=uuid.uuid4(),
            title="Software Engineer",
            company="Tech Corp",
            location="Remote",
            description="BS or equivalent in Computer Science.",
        )

        result = matcher.match(sample_candidate, job)
        assert result.highest_degree == "Bachelor's"
        assert result.score >= 90.0
