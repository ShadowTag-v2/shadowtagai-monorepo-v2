from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_ID: str = "shadowtag-omega-v4"
    ENVIRONMENT: str = "production"
    # KMS keys & Secrets
    FERNET_KEY: str = ""  # Used for local encryption of payload values
    GCP_KMS_KEY_RING: str = ""
    GCP_KMS_KEY_NAME: str = ""

    # DB
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/legaltrack"

    class Config:
        env_file = ".env"


settings = Settings()
