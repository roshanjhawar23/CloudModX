from typing import Optional
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "CloudModX"
    PROJECT_DESCRIPTION: str = "College Cloud-Native Module Lifecycle Management Platform"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Environment & Secrets
    ENVIRONMENT: str = "development"
    # Local development secret key; MUST be overridden with a cryptographically strong secret in production
    SECRET_KEY: str = "cloudmodx-local-dev-secret-key-replace-in-production-32chars"
    # Host development connects to local Docker PostgreSQL on mapped port 5433.
    # When running inside Docker Compose, this is overridden via DATABASE_URL to @db:5432.
    # In production, this MUST point to the managed Amazon RDS endpoint.
    DATABASE_URL: Optional[str] = "postgresql+psycopg2://cloudmodx_user:cloudmodx_password@127.0.0.1:5433/cloudmodx_db"

    # AWS & S3 Settings
    AWS_REGION: str = "ap-south-1"
    # Leave empty to store artifacts on local disk (default for local development).
    # Set to your own bucket (Terraform output `artifact_bucket_name`) to use Amazon S3.
    ARTIFACT_BUCKET_NAME: str = ""
    # Set to true to print every SQL statement (very noisy)
    SQL_ECHO: bool = False
    LOCAL_STORAGE_PATH: str = "/tmp/cloudmodx-artifacts"

    # CORS Settings
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost",
        "http://localhost:80",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1",
        "http://127.0.0.1:80",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_production_configuration(self) -> "Settings":
        """Enforce strict configuration requirements when running in production."""
        if self.ENVIRONMENT.lower() == "production":
            weak_secret_indicators = [
                "insecure",
                "change-me",
                "placeholder",
                "local-dev",
                "replace-in-production",
                "replace-in-prod",
            ]
            if (
                not self.SECRET_KEY
                or len(self.SECRET_KEY) < 32
                or any(ind in self.SECRET_KEY.lower() for ind in weak_secret_indicators)
            ):
                raise ValueError(
                    "Production configuration error: SECRET_KEY must be a cryptographically secure random string with at least 32 characters."
                )
            if (
                not self.DATABASE_URL
                or "localhost" in self.DATABASE_URL.lower()
                or "127.0.0.1" in self.DATABASE_URL
                or "change-me" in self.DATABASE_URL.lower()
            ):
                raise ValueError(
                    "Production configuration error: DATABASE_URL must point to an external production database (e.g., Amazon RDS), not localhost."
                )
        return self

    @property
    def sync_database_url(self) -> Optional[str]:
        """Ensure the PostgreSQL database URL always specifies the psycopg2 driver."""
        if not self.DATABASE_URL:
            return None
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg2://", 1)
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+psycopg2://", 1)
        return url


settings = Settings()
