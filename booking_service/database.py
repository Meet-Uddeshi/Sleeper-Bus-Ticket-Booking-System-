from supabase import create_client, Client
from booking_service.core.config import settings
from booking_service.core.logger import logger

url: str = settings.SUPABASE_URL
key: str = settings.SUPABASE_KEY

if not url or not key:
    logger.critical("SUPABASE_URL or SUPABASE_KEY missing in settings!")

try:
    supabase: Client = create_client(url, key)
    logger.info("Supabase client initialized successfully.")
except Exception as e:
    logger.exception(f"Failed to initialize Supabase client: {e}")
    raise e
