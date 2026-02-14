"""Configuration settings for the application."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    gemini_api_key: str
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings instance.

    Returns:
        Settings: Application settings

    Raises:
        ValidationError: If required environment variables are missing
    """
    return Settings()
