import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # --- Service Info ---
    SERVICE_NAME: str = Field(default="base-service")
    LOG_LEVEL: str = "INFO"
    
    # --- Database Keys (Loaded from .env) ---
    SUPABASE_URL: str = Field(..., description="Supabase URL")
    SUPABASE_KEY: str = Field(..., description="Supabase Anon Key")

    # --- API URLs (CRITICAL FIX FOR FRONTEND) ---
    # These point to your local microservices
    BOOKING_API_URL: str = Field(default="http://127.0.0.1:8000/api/v1")
    PREDICTION_API_URL: str = Field(default="http://127.0.0.1:8001")

    # --- Paths ---
    # Calculates root directory dynamically
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LOG_DIR: str = os.path.join(BASE_DIR, "logs")

    # --- Pydantic V2 Configuration ---
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignores extra variables in .env
    )

settings = Settings()