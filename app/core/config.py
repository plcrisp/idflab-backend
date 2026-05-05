from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "IDFLab"
    DATABASE_URL: str
    REDIS_URL: str
    CORS_ORIGINS: list[str] = ["http://localhost:4200"]

    SECRET_KEY: str 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 20
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    RESEND_API_KEY: str
    VERIFY_EMAIL_TEMPLATE_ID: str
    RESET_PASSWORD_TEMPLATE_ID: str

    GOOGLE_CLIENT_ID: str

    model_config = ConfigDict(
        env_file=".env",
        extra="ignore" 
    )

settings = Settings()

