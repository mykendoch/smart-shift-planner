"""
Configuration Settings Management

This module loads all application settings from environment variables (.env file).
Provides centralized configuration for database, security, logging, and business rules.
All settings are validated by Pydantic on application startup.

Environment variables (.env file):
    DATABASE_URL=postgresql://postgres:Ndoch@localhost:5432/gigeconomy
    PROJECT_NAME=Smart Shift Planner
    GUARANTEE_THRESHOLD=0.9
    DEBUG=True
    ENVIRONMENT=development
"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """
    Application Settings - Centralized Configuration
    
    Loaded from .env file using Pydantic validation.
    Missing values use defaults provided here.
    
    Benefits of this approach:
    - Secrets (passwords, API keys) kept out of source code
    - Different settings for dev/test/production environments
    - Type-safe configuration (Pydantic validates on startup)
    """
    model_config = ConfigDict(env_file=".env", case_sensitive=True)
    
    # ========================================================================
    # DATABASE CONFIGURATION
    # ========================================================================
    # PostgreSQL connection string format:
    # postgresql://username:password@hostname:port/database_name
    # Example: postgresql://postgres:Ndoch@localhost:5432/gigeconomy
    DATABASE_URL: str
    
    # ========================================================================
    # SECURITY SETTINGS (For future JWT authentication)
    # ========================================================================
    # SECRET_KEY: Random string for signing JWT tokens (keep secret in production!)
    # ALGORITHM: JWT signing algorithm (HS256 is standard)
    # ACCESS_TOKEN_EXPIRE_MINUTES: How long JWT tokens remain valid before re-login required
    SECRET_KEY: str
    ALGORITHM: str = \"HS256\"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    
    # ========================================================================
    # APPLICATION SETTINGS
    # ========================================================================\n    PROJECT_NAME: str = \"Smart Shift Planner\"
    VERSION: str = \"1.0.0\"
    ENVIRONMENT: str = \"development\"  # Options: development, testing, production
    DEBUG: bool = True  # When True, enables SQL logging and detailed error messages
    LOG_LEVEL: str = \"INFO\"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    # ========================================================================
    # BUSINESS RULES - Income Guarantee Mechanism
    # ========================================================================
    # GUARANTEE_THRESHOLD: Income guarantee percentage (0.9 = 90%)
    #   Top-up = max(0, predicted_earnings × THRESHOLD - actual_earnings)
    #   Example: If predicted=$100, actual=$80, threshold=0.9
    #   Top-up = max(0, 100×0.9 - 80) = max(0, 10) = $10 paid to worker
    GUARANTEE_THRESHOLD: float = 0.9
    
    # MINIMUM_HOURS_FOR_GUARANTEE: Minimum shift length qualifying for guarantee
    # Shifts shorter than this won't receive top-up even if earnings fall short
    MINIMUM_HOURS_FOR_GUARANTEE: float = 4.0


# Create settings instance
settings = Settings()