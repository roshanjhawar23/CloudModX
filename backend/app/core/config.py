from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "CloudModX"
    PROJECT_DESCRIPTION: str = "College Cloud-Native Module Lifecycle Management Platform"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Environment & Secrets (Never hardcoded)
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "insecure-secret-key-change-in-production"
    DATABASE_URL: Optional[str] = "postgresql+psycopg2://cloudmodx_user:cloudmodx_password@127.0.0.1:5433/cloudmodx_db"

    # AWS & S3 Settings
    AWS_REGION: str = "ap-south-1"
    ARTIFACT_BUCKET_NAME: str = "cloudmodx-artifacts-development-7e20711b318423260d00ea711f"
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
