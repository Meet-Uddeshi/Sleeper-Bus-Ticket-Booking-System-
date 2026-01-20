from pydantic_settings import BaseSettings
from pydantic import Field
import os

class Settings(BaseSettings):
    SERVICE_NAME: str = "prediction-svc"
    LOG_LEVEL: str = "INFO"
    
    # Prediction service doesn't need Supabase currently, but good to have consistent class
    
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LOG_DIR: str = os.path.join(os.path.dirname(BASE_DIR), "logs")

    class Config:
        env_file = ".env"

settings = Settings()
