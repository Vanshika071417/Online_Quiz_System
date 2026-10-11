"""
Configuration module for the Online Quiz System.
Supports PostgreSQL (production) with automatic SQLite fallback for local development.
"""

import os
from typing import List
from pydantic import BaseModel

class Settings(BaseModel):
    APP_NAME: str = "Online Quiz System - Production Assessment Engine"
    API_V1_STR: str = "/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "prod-assessment-secret-key-change-in-env-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    
    # Authoritative Database (PostgreSQL recommended; SQLite fallback for local dev)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./quiz_system.db")
    
    # Tenancy defaults
    DEFAULT_TENANT_ID: str = "tenant-prod-root"
    DEFAULT_TENANT_NAME: str = "Enterprise Academic Institution"
    
    # Assessment integrity & timeouts
    DEFAULT_AUTOSAVE_MAX_PAYLOAD_BYTES: int = 65536  # 64 KB per answer
    DEFAULT_GRACE_PERIOD_SECONDS: int = 15  # Network transit grace period for submit
    
    CORS_ORIGINS: List[str] = ["*"]

settings = Settings()
