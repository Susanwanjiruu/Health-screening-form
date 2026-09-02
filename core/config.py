import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Single-Center Health Screening System"
    API_V1_STR: str = "/api/v1"

  
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://localhost/compassion_db")

  
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev_local_secret_signing_key_fallback_123")
    ALGORITHM: str = "HS256"
    SESSION_TOKEN_MINUTES: int = 15
    REFRESH_TOKEN_DAYS: int = 7
    ACCESS_CODE_VALID_DAYS: int = 7
    RESET_TOKEN_VALID_MINUTES: int = 30
    LOGIN_OTP_VALID_MINUTES: int = 5

    
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", "no-reply@yourcenter.org")
    SMTP_FROM_NAME: str = os.getenv("SMTP_FROM_NAME", "Health Screening Center")

  
    CARBONE_API_KEY: str = os.getenv("CARBONE_API_KEY", "")
    CARBONE_API_BASE_URL: str = os.getenv("CARBONE_API_BASE_URL", "https://api.carbone.io")
    CARBONE_REPORT_TEMPLATE_ID: str = os.getenv("CARBONE_REPORT_TEMPLATE_ID", "")

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
