import asyncio
import os
import shutil
import tempfile
import uuid
from typing import AsyncGenerator
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import models  # Ensure all SQLAlchemy models are registered
from models.base import Base
from core.dependencies import get_db, get_storage
from core.storage.local import LocalStorageProvider
from main import app

TEST_DB_FILE = "./test_job_copilot.db"
test_engine = create_async_engine(f"sqlite+aiosqlite:///{TEST_DB_FILE}", echo=False)
TestSessionFactory = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

DEMO_USER_ID = uuid.UUID("a0000000-0000-0000-0000-000000000001")


@pytest.fixture(scope="session")
def event_loop():
    """Create session-scoped event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def init_test_db():
    """Initialize SQLite tables and seed demo user for hermetic testing."""
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except OSError:
            pass

    async with test_engine.begin() as conn:
        from sqlalchemy import text
        await conn.execute(text("PRAGMA journal_mode=WAL;"))
        await conn.run_sync(Base.metadata.create_all)


    # Seed initial test demo user
    async with TestSessionFactory() as session:
        user = models.UserModel(
            id=DEMO_USER_ID,
            name="Alex Chen",
            email="alex.chen@example.com",
        )
        session.add(user)
        profile = models.ProfileModel(
            id=uuid.UUID("b0000000-0000-0000-0000-000000000001"),
            user_id=DEMO_USER_ID,
            preferred_roles=["Staff Software Engineer"],
            preferred_locations=["Remote"],
            years_of_experience=8,
        )
        session.add(profile)
        await session.commit()

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()

    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except OSError:
            pass


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Function-level test session."""
    async with TestSessionFactory() as session:
        yield session


@pytest.fixture(scope="function", autouse=True)
async def cleanup_test_data():
    """Ensure database state is clean before each test."""
    async with TestSessionFactory() as session:
        from sqlalchemy import text
        await session.execute(text("DELETE FROM skills;"))
        await session.execute(text("DELETE FROM projects;"))
        await session.execute(text("DELETE FROM education;"))
        await session.execute(text("DELETE FROM experience;"))
        await session.execute(text("DELETE FROM certifications;"))
        await session.execute(text("DELETE FROM resumes;"))
        await session.commit()
    yield
    async with TestSessionFactory() as session:
        from sqlalchemy import text
        await session.execute(text("DELETE FROM skills;"))
        await session.execute(text("DELETE FROM projects;"))
        await session.execute(text("DELETE FROM education;"))
        await session.execute(text("DELETE FROM experience;"))
        await session.execute(text("DELETE FROM certifications;"))
        await session.execute(text("DELETE FROM resumes;"))
        await session.commit()



@pytest.fixture(scope="function")
def temp_storage():
    """Isolated temporary directory for storage tests."""
    temp_dir = tempfile.mkdtemp(prefix="test_uploads_")
    provider = LocalStorageProvider(base_dir=temp_dir)
    yield provider, temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession, temp_storage) -> AsyncGenerator[AsyncClient, None]:
    """
    Async HTTP test client bound to FastAPI application with test DB and isolated temp storage.
    """
    provider, _ = temp_storage

    async def override_get_db():
        async with TestSessionFactory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise



    def override_get_storage():
        return provider

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_storage] = override_get_storage

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

    app.dependency_overrides.clear()
