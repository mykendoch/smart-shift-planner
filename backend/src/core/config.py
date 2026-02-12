"""
Configuration Settings
Loads settings from environment variables
"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Application settings loaded from .env file"""
    model_config = ConfigDict(env_file=".env", case_sensitive=True)
    
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    
    # Application
    PROJECT_NAME: str = "Smart Shift Planner"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Business Rules
    GUARANTEE_THRESHOLD: float = 0.9
    MINIMUM_HOURS_FOR_GUARANTEE: float = 4.0


# Create settings instance
settings = Settings()