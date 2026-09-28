import uuid
from unittest.mock import AsyncMock, patch
import pytest
from httpx import AsyncClient
from core.jobs.providers.base import RawJob
from core.jobs.providers.registry import job_provider_registry
from main import app


@pytest.fixture(autouse=True)
def mock_provider_network_calls():
    """Ensure integration tests use deterministic test jobs without network latency."""
    mock_jobs = [
        RawJob(
            source="RemoteOK",
            external_id="rok-test-1",
            title="Senior Python Architect",
            company="Tech Corp",
            location="Remote",
            description="Build high-performance FastAPI microservices with PostgreSQL and Docker.",
            apply_url="https://techcorp.com/jobs/1",
            employment_type="Full-time",
            salary_min=140000,
            salary_max=180000,
            currency="USD",
            raw_skills=["Python", "FastAPI", "PostgreSQL"],
        ),
        RawJob(
            source="Greenhouse",
            external_id="gh-test-2",
            title="Staff Frontend Engineer",
            company="Figma",
            location="San Francisco, CA (Remote)",
            description="Craft Next.js and React 19 web applications with TypeScript and Tailwind CSS.",
            apply_url="https://figma.com/jobs/2",
            employment_type="Full-time",
            salary_min=150000,
            salary_max=195000,
            currency="USD",
            raw_skills=["TypeScript", "React", "Next.js"],
        ),
        RawJob(
            source="Lever",
            external_id="lever-test-3",
            title="DevOps Lead Engineer",
            company="Postman",
            location="Remote",
            description="Manage Kubernetes clusters, Terraform infrastructure, and Docker deployments on AWS.",
            apply_url="https://postman.com/jobs/3",
            employment_type="Full-time",
            salary_min=135000,
            salary_max=175000,
            currency="USD",
            raw_skills=["Kubernetes", "Docker", "AWS", "Terraform"],
        ),
        RawJob(
            source="Wellfound",
            external_id="wf-test-4",
            title="Founding AI Engineer",
            company="Cognition",
            location="New York, NY",
            description="Train and evaluate autonomous coding agents with PyTorch and Python.",
            apply_url="https://cognition.com/jobs/4",
            employment_type="Full-time",
            salary_min=160000,
            salary_max=220000,
            currency="USD",
            raw_skills=["Python", "PyTorch", "AI/ML"],
        ),
    ]

    with patch.object(
        job_provider_registry.get_provider("remoteok"), "fetch_jobs", new_callable=AsyncMock
    ) as mock_rok, patch.object(
        job_provider_registry.get_provider("greenhouse"), "fetch_jobs", new_callable=AsyncMock
    ) as mock_gh, patch.object(
        job_provider_registry.get_provider("lever"), "fetch_jobs", new_callable=AsyncMock
    ) as mock_lev, patch.object(
        job_provider_registry.get_provider("wellfound"), "fetch_jobs", new_callable=AsyncMock
    ) as mock_wf:
        mock_rok.return_value = [mock_jobs[0]]
        mock_gh.return_value = [mock_jobs[1]]
        mock_lev.return_value = [mock_jobs[2]]
        mock_wf.return_value = [mock_jobs[3]]
        yield



@pytest.mark.asyncio
async def test_job_sync_and_deduplication(client: AsyncClient):
    """
    Test job synchronization across providers and subsequent deduplication.
    """
    # First sync: ingest jobs
    resp = await client.post("/api/v1/jobs/sync", json={"limitPerSource": 5})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["syncedCount"] > 0
    assert data["durationMs"] >= 0
    assert len(data["sources"]) > 0

    first_synced = data["syncedCount"]

    # Second sync: should deduplicate already ingested jobs
    resp2 = await client.post("/api/v1/jobs/sync", json={"limitPerSource": 5})
    assert resp2.status_code == 200
    data2 = resp2.json()["data"]
    assert data2["duplicatesSkipped"] >= first_synced


@pytest.mark.asyncio
async def test_list_jobs_pagination(client: AsyncClient):
    """
    Test listing jobs with pagination.
    """
    # Ensure some jobs are present
    await client.post("/api/v1/jobs/sync", json={"limitPerSource": 3})

    resp = await client.get("/api/v1/jobs?page=1&pageSize=5")
    assert resp.status_code == 200
    res_data = resp.json()["data"]
    assert "items" in res_data
    assert "total" in res_data
    assert res_data["page"] == 1
    assert res_data["pageSize"] == 5
    assert len(res_data["items"]) <= 5

    # Check job fields
    first_job = res_data["items"][0]
    assert "id" in first_job
    assert "title" in first_job
    assert "company" in first_job
    assert "location" in first_job
    assert "source" in first_job
    assert "applyUrl" in first_job


@pytest.mark.asyncio
async def test_search_jobs_with_filters(client: AsyncClient):
    """
    Test faceted search across role, location, source, and salary.
    """
    await client.post("/api/v1/jobs/sync", json={"limitPerSource": 5})

    # Search by general query
    resp_q = await client.get("/api/v1/jobs/search?query=engineer")
    assert resp_q.status_code == 200
    assert "items" in resp_q.json()["data"]

    # Search by location = remote
    resp_loc = await client.get("/api/v1/jobs/search?location=Remote")
    assert resp_loc.status_code == 200
    for job in resp_loc.json()["data"]["items"]:
        assert "remote" in job["location"].lower()

    # Search by source = RemoteOK
    resp_src = await client.get("/api/v1/jobs/search?source=RemoteOK")
    assert resp_src.status_code == 200
    for job in resp_src.json()["data"]["items"]:
        assert job["source"].lower() == "remoteok"

    # Search by minimum salary
    resp_sal = await client.get("/api/v1/jobs/search?minSalary=100000&sortBy=highest_salary")
    assert resp_sal.status_code == 200
    items = resp_sal.json()["data"]["items"]
    if items:
        # Check salary condition
        for j in items:
            s_max = j.get("salaryMax")
            s_min = j.get("salaryMin")
            assert (s_max is not None and s_max >= 100000) or (s_min is not None and s_min >= 100000)


@pytest.mark.asyncio
async def test_get_job_by_id(client: AsyncClient):
    """
    Test retrieving full details of a specific job by UUID.
    """
    await client.post("/api/v1/jobs/sync", json={"limitPerSource": 2})

    list_resp = await client.get("/api/v1/jobs?pageSize=1")
    items = list_resp.json()["data"]["items"]
    assert len(items) > 0
    job_id = items[0]["id"]

    # Fetch details
    detail_resp = await client.get(f"/api/v1/jobs/{job_id}")
    assert detail_resp.status_code == 200
    job = detail_resp.json()["data"]
    assert job["id"] == job_id
    assert "skills" in job
    assert isinstance(job["skills"], list)

    # 404 for non-existent job UUID
    random_id = str(uuid.uuid4())
    not_found_resp = await client.get(f"/api/v1/jobs/{random_id}")
    assert not_found_resp.status_code == 404
