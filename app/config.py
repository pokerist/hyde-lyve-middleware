from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Application settings
    app_name: str = "Hydepark Lyve Middleware"
    app_version: str = "1.0.0"
    debug: bool = False
    port: int = 3000
    host: str = "0.0.0.0"
    
    # Database settings
    database_url: str = "postgresql+asyncpg://user:password@localhost/hyde_lyve"
    
    # Redis settings
    redis_url: str = "redis://localhost:6379/0"
    
    # HikCentral settings
    hikcentral_base_url: str = "https://192.168.1.101/artemis"
    hikcentral_app_key: str = "27108141"
    hikcentral_app_secret: str = "c3U7KikkPGo2Yka6GMZ5"
    hikcentral_user_id: str = "admin"
    hikcentral_org_index_code: str = "1"
    hikcentral_verify_ssl: bool = False
    
    # Security settings
    api_key: str = "demo-key"
    require_api_key: bool = True
    
    # Circuit breaker settings
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_recovery_timeout: int = 60  # seconds
    
    # API settings
    qr_code_validity_minutes: int = 60
    qr_code_image_size: int = 300
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()