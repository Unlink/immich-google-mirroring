"""Configuration settings for the application."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings"""
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8080
    
    # Security
    app_secret_key: str = "changeme-generate-random-key"
    
    # Database
    database_path: str = "/data/app.db"
    
    # URLs
    base_url: str = "http://localhost:8080"
    
    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    
    # Logs
    log_path: str = "/data/logs"
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
