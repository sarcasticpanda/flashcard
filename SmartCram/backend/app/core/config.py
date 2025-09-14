"""
Configuration settings for the SMARTCRAM application.
Uses Pydantic settings for type-safe environment variable handling.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    database_url: str = Field(
        default="mysql+mysqlconnector://smartcram:smartpass@localhost:3306/smartcram",
        description="SQLAlchemy database URL"
    )
    
    # OpenAI Configuration
    openai_api_key: str = Field(
        ...,  # Required field
        description="OpenAI API key for content generation"
    )
    
    # JWT Configuration
    jwt_secret_key: str = Field(
        default="smartcram-secret-key-change-in-production",
        description="Secret key for JWT token signing"
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="JWT signing algorithm"
    )
    access_token_expire_minutes: int = Field(
        default=720,  # 12 hours
        description="JWT token expiration time in minutes"
    )
    
    # Application Configuration
    api_base_url: str = Field(
        default="http://localhost:8000",
        description="Base URL for the API"
    )
    debug: bool = Field(
        default=True,
        description="Enable debug mode"
    )
    environment: str = Field(
        default="development",
        description="Application environment"
    )
    
    # CORS Configuration
    allowed_origins: List[str] = Field(
        default=["http://localhost:8080", "http://localhost:3000"],
        description="Allowed CORS origins"
    )
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(
        default=60,
        description="Rate limit requests per minute"
    )
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create global settings instance
settings = Settings()
