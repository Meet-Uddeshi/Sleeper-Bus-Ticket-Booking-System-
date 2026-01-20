from pydantic_settings import BaseSettings
from pydantic import Field
import os

class Settings(BaseSettings):
    # Service Info
    SERVICE_NAME: str = "booking-svc"
    LOG_LEVEL: str = "INFO"
    
    # Database
    SUPABASE_URL: str = Field(..., description="Supabase URL")
    SUPABASE_KEY: str = Field(..., description="Supabase Service Role/Anon Key")

    # We can rely on absolute path or relative to workspace. 
    # Let's assume the user runs from service dir, so we go up one level.
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LOG_DIR: str = os.path.join(os.path.dirname(BASE_DIR), "logs")

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
