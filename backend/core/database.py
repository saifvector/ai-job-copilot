import time
from typing import AsyncGenerator, Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)

# Ensure URL uses asyncpg for PostgreSQL
db_url = settings.DATABASE_URL
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)

# Strip Prisma-specific query parameters like ?schema=public incompatible with asyncpg
if "?" in db_url:
    import urllib.parse
    parsed = urllib.parse.urlparse(db_url)
    query_params = urllib.parse.parse_qs(parsed.query)
    query_params.pop("schema", None)
    new_query = urllib.parse.urlencode(query_params, doseq=True)
    db_url = urllib.parse.urlunparse(parsed._replace(query=new_query))

# Configure engine arguments
engine_kwargs: Dict[str, Any] = {
    "echo": settings.DATABASE_ECHO,
    "future": True,
}

# Connection pool settings for PostgreSQL
if "sqlite" not in db_url:
    engine_kwargs.update({
        "pool_size": settings.DATABASE_POOL_SIZE,
        "max_overflow": settings.DATABASE_MAX_OVERFLOW,
        "pool_pre_ping": True,
        "pool_recycle": 1800,
    })

engine: AsyncEngine = create_async_engine(db_url, **engine_kwargs)

AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


async def init_db() -> None:
    """
    Initialize database schema tables if running in development or SQLite fallback.
    """
    import models
    from models import Base, ProfileModel, UserModel
    import uuid

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Ensure demo user exists for seamless development/testing
        async with AsyncSessionFactory() as session:
            stmt = text("SELECT id FROM users WHERE id = :user_id")
            demo_id = uuid.UUID("a0000000-0000-0000-0000-000000000001")
            result = await session.execute(stmt, {"user_id": str(demo_id)})
            existing = result.scalar_one_or_none()
            if not existing:
                demo_user = UserModel(
                    id=demo_id,
                    name="Alex Chen",
                    email="alex.chen@example.com",
                )
                session.add(demo_user)
                demo_profile = ProfileModel(
                    id=uuid.UUID("b0000000-0000-0000-0000-000000000001"),
                    user_id=demo_id,
                    preferred_roles=["Staff Software Engineer", "Full Stack Architect"],
                    preferred_locations=["Remote", "San Francisco, CA"],
                    years_of_experience=8,
                )
                session.add(demo_profile)
                await session.commit()
                logger.info(f"Initialized demo user ({demo_id}) for development.")
    except Exception as exc:
        logger.warning(f"Database schema auto-init skipped or failed: {exc}")


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an active transactional async database session.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Alias for dependency consistency across endpoints
get_db = get_db_session


async def check_database_health() -> Dict[str, Any]:
    """
    Execute a lightweight ping to verify database connectivity and measure latency.
    """
    start_time = time.perf_counter()
    try:
        async with AsyncSessionFactory() as session:
            await session.execute(text("SELECT 1"))
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return {
            "connected": True,
            "latency_ms": latency_ms,
            "status": "healthy",
        }
    except Exception as exc:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.warning(f"Database health check failed: {exc}")
        return {
            "connected": False,
            "latency_ms": latency_ms,
            "status": "unhealthy",
            "error": str(exc),
        }
