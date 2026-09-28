from functools import lru_cache
from typing import List, Literal, Union
from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Core application configuration and environment settings.
    Loads values from environment variables or .env file.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Core App Meta
    PROJECT_NAME: str = "AI Job Copilot API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["development", "staging", "production", "test"] = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Security
    SECRET_KEY: str = Field(
        default="development-insecure-secret-key-at-least-32-chars-long",
        description="Secret key for cryptographical signatures"
    )
    ALLOWED_HOSTS: List[str] = ["*"]
    CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        return ["http://localhost:3000"]

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/job_copilot_dev",
        description="Async PostgreSQL connection URL"
    )
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_TIMEOUT: int = 30

    # Logging
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FORMAT: Literal["console", "json"] = "console"

    # AI Model Strategy (Gemini Intelligence Engine)
    GEMINI_API_KEY: str = Field(
        default="",
        description="Google Gemini API Key for Resume Intelligence Engine"
    )
    GEMINI_PRIMARY_MODEL: str = Field(
        default="gemini-2.5-pro",
        description="Primary model for resume parsing"
    )
    GEMINI_FALLBACK_MODEL: str = Field(
        default="gemini-2.5-flash",
        description="Fallback model for resume parsing"
    )
    AI_REQUEST_TIMEOUT: int = Field(
        default=45,
        description="Timeout in seconds for AI inference requests"
    )

    # Matching Engine Weights (Phase 5 Default Weights: Skills 50%, Experience 20%, Role 15%, Location 10%, Education 5%)
    MATCH_WEIGHT_SKILLS: float = Field(
        default=0.50,
        description="Weight for skill match score (0.0 to 1.0)"
    )
    MATCH_WEIGHT_EXPERIENCE: float = Field(
        default=0.20,
        description="Weight for experience alignment score (0.0 to 1.0)"
    )
    MATCH_WEIGHT_ROLE: float = Field(
        default=0.15,
        description="Weight for role title alignment score (0.0 to 1.0)"
    )
    MATCH_WEIGHT_LOCATION: float = Field(
        default=0.10,
        description="Weight for location alignment score (0.0 to 1.0)"
    )
    MATCH_WEIGHT_EDUCATION: float = Field(
        default=0.05,
        description="Weight for education alignment score (0.0 to 1.0)"
    )
    MATCH_MIN_SCORE_THRESHOLD: float = Field(
        default=0.0,
        description="Minimum score threshold for matching results filtering"
    )

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()


settings = get_settings()
