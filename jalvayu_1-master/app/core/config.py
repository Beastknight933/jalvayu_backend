from typing import Any, Dict, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings managed by Pydantic.
    Loads from .env file or environment variables.
    """
    PROJECT_NAME: str = "Climate Digital Twin API"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Database Settings
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str = "5432"
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: Any) -> Any:
        if isinstance(v, str):
            return v
        values = info.data
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=int(values.get("POSTGRES_PORT", 5432)),
            path=f"{values.get('POSTGRES_DB', '')}",
        )

    # Redis Settings
    REDIS_HOST: str
    REDIS_PORT: str

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    # JWT Authentication Settings
    PRIVATE_KEY: str
    PUBLIC_KEY: str
    ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Celery Settings
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # External APIs (Climate Datasets & Services)
    IMD_API_URL: Optional[str] = None
    IMD_API_KEY: Optional[str] = None
    
    ISRO_BHUVAN_URL: Optional[str] = None
    ISRO_API_KEY: Optional[str] = None

    DIGITAL_TWIN_SIMULATION_URL: Optional[str] = None
    ML_INFERENCE_SERVICE_URL: Optional[str] = None
    ML_MODEL_REGISTRY_KEY: Optional[str] = None

    # Storage Settings
    DATA_STORAGE_BASE_PATH: str = "/app/data"
    DATA_RAW_DIR: str = "raw"
    DATA_PROCESSED_DIR: str = "processed"
    DATA_MODELS_DIR: str = "models"
    DATA_SIMULATIONS_DIR: str = "simulations"
    DATA_CACHE_DIR: str = "cache"
    DATA_EXPORTS_DIR: str = "exports"
    
    STORAGE_BACKEND: str = "local" # options: "local", "s3"
    S3_BUCKET_NAME: Optional[str] = None
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")


settings = Settings()
