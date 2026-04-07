from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "IDFLab"
    DATABASE_URL: str
    REDIS_URL: str
    CORS_ORIGINS: list[str] = ["http://localhost:4200"]

    model_config = ConfigDict(
        env_file=".env",
        extra="ignore" 
    )

settings = Settings()

