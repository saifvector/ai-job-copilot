import pytest
from core.jobs.pipeline.deduplicator import JobDeduplicator
from core.jobs.pipeline.normalizer import JobNormalizer
from core.jobs.pipeline.validator import JobValidator
from core.jobs.providers.base import RawJob


def test_location_normalization():
    # Exact and casing matches
    assert JobNormalizer.normalize_location("Remote") == "Remote"
    assert JobNormalizer.normalize_location("REMOTE") == "Remote"
    assert JobNormalizer.normalize_location("remote") == "Remote"
    assert JobNormalizer.normalize_location("worldwide") == "Remote"
    assert JobNormalizer.normalize_location("telecommute") == "Remote"
    assert JobNormalizer.normalize_location("Worldwide (Remote)") == "Remote"

    # Hybrid locations
    hybrid = JobNormalizer.normalize_location("San Francisco, CA / Remote")
    assert "Remote" in hybrid
    assert "San Francisco" in hybrid

    # City without remote
    city = JobNormalizer.normalize_location("New York, NY")
    assert city == "New York, NY"

    # Empty fallback
    assert JobNormalizer.normalize_location("") == "Remote"
    assert JobNormalizer.normalize_location(None) == "Remote"


def test_employment_type_normalization():
    assert JobNormalizer.normalize_employment_type("Full-time") == "Full-time"
    assert JobNormalizer.normalize_employment_type("FULLTIME") == "Full-time"
    assert JobNormalizer.normalize_employment_type("full_time") == "Full-time"
    assert JobNormalizer.normalize_employment_type("Permanent") == "Full-time"
    assert JobNormalizer.normalize_employment_type("regular") == "Full-time"

    assert JobNormalizer.normalize_employment_type("part-time") == "Part-time"
    assert JobNormalizer.normalize_employment_type("Contractor") == "Contract"
    assert JobNormalizer.normalize_employment_type("internship") == "Internship"
    assert JobNormalizer.normalize_employment_type(None) == "Full-time"


def test_salary_and_url_normalization():
    s_min, s_max, curr = JobNormalizer.normalize_salary(150000, 120000, "usd")
    assert s_min == 120000.0
    assert s_max == 150000.0
    assert curr == "USD"

    # URL tracking stripping
    clean_url = JobNormalizer.normalize_url("https://company.com/jobs/123/?utm_source=linkedin&utm_medium=feed/")
    assert clean_url == "https://company.com/jobs/123"


def test_job_validator():
    valid_job = RawJob(
        source="RemoteOK",
        external_id="101",
        title="Senior Python Architect",
        company="Tech Corp",
        location="Remote",
        description="Detailed description for high-scale backend services in Python and FastAPI.",
        apply_url="https://techcorp.com/apply/101",
    )
    is_valid, error = JobValidator.validate(valid_job)
    assert is_valid is True
    assert error is None

    # Invalid title
    bad_title = RawJob(
        source="RemoteOK",
        external_id="102",
        title="",
        company="Tech Corp",
        location="Remote",
        description="Detailed description.",
        apply_url="https://techcorp.com/apply",
    )
    is_valid, error = JobValidator.validate(bad_title)
    assert is_valid is False
    assert "title" in error.lower()


def test_job_deduplicator():
    key1 = JobDeduplicator.generate_dedup_key(
        company="Stripe",
        title="Software Engineer",
        apply_url="https://stripe.com/jobs/101?utm_source=feed",
    )
    key2 = JobDeduplicator.generate_dedup_key(
        company="stripe",
        title="Software Engineer",
        apply_url="https://stripe.com/jobs/101",
    )
    # Different case and tracking params produce exact same deduplication key
    assert key1 == key2

    job_a = RawJob(
        source="RemoteOK",
        external_id="1",
        title="Staff Engineer",
        company="Vercel",
        location="Remote",
        description="Job A description.",
        apply_url="https://vercel.com/jobs/1",
    )
    job_b = RawJob(
        source="Greenhouse",
        external_id="2",
        title="Staff Engineer",
        company="Vercel",
        location="Remote",
        description="Job B description.",
        apply_url="https://vercel.com/jobs/1",
    )

    seen = set()
    filtered, skipped = JobDeduplicator.filter_batch_duplicates([job_a, job_b], seen)
    assert len(filtered) == 1
    assert skipped == 1
