import pytest
from core.jobs.providers.base import JobProvider, RawJob
from core.jobs.providers.greenhouse import GreenhouseProvider
from core.jobs.providers.lever import LeverProvider
from core.jobs.providers.registry import job_provider_registry
from core.jobs.providers.remoteok import RemoteOKProvider
from core.jobs.providers.wellfound import WellfoundProvider


@pytest.mark.asyncio
async def test_remoteok_provider_fetch():
    provider = RemoteOKProvider()
    assert provider.name == "RemoteOK"
    assert isinstance(provider, JobProvider)

    jobs = await provider.fetch_jobs(limit=5)
    assert len(jobs) > 0
    first_job = jobs[0]
    assert isinstance(first_job, RawJob)
    assert first_job.source == "RemoteOK"
    assert first_job.title
    assert first_job.company
    assert first_job.apply_url.startswith("http")


@pytest.mark.asyncio
async def test_greenhouse_provider_fetch():
    provider = GreenhouseProvider()
    assert provider.name == "Greenhouse"

    jobs = await provider.fetch_jobs(limit=5)
    assert len(jobs) > 0
    first_job = jobs[0]
    assert first_job.source == "Greenhouse"
    assert first_job.title
    assert first_job.company
    assert first_job.apply_url.startswith("http")


@pytest.mark.asyncio
async def test_lever_provider_fetch():
    provider = LeverProvider()
    assert provider.name == "Lever"

    jobs = await provider.fetch_jobs(limit=5)
    assert len(jobs) > 0
    first_job = jobs[0]
    assert first_job.source == "Lever"
    assert first_job.title
    assert first_job.company


@pytest.mark.asyncio
async def test_wellfound_provider_fetch():
    provider = WellfoundProvider()
    assert provider.name == "Wellfound"

    jobs = await provider.fetch_jobs(limit=5)
    assert len(jobs) > 0
    first_job = jobs[0]
    assert first_job.source == "Wellfound"
    assert first_job.title
    assert first_job.company
    assert len(first_job.raw_skills) > 0


def test_job_provider_registry():
    providers = job_provider_registry.list_providers()
    assert len(providers) >= 4

    names = job_provider_registry.provider_names()
    assert "RemoteOK" in names
    assert "Greenhouse" in names
    assert "Lever" in names
    assert "Wellfound" in names

    assert job_provider_registry.get_provider("remoteok") is not None
    assert job_provider_registry.get_provider("non_existent") is None
