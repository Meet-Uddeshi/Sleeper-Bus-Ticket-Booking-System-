from loguru import logger
import sys
import os
from .config import settings

# Configure Loguru
def configure_logging():
    logger.remove() # Remove default handler
    
    # 1. Console Handler (Colored, for Dev)
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
        serialize=False # Friendly text format
    )

    # 2. File Handler (JSON, Shared, Rotated)
    # Ensure log directory exists
    os.makedirs(settings.LOG_DIR, exist_ok=True)
    
    log_file_path = os.path.join(settings.LOG_DIR, f"{settings.SERVICE_NAME}_{{time:YYYY-MM-DD}}.log")
    
    logger.add(
        log_file_path,
        rotation="10 MB",
        retention="30 days",
        level=settings.LOG_LEVEL,
        serialize=True, # JSON Format
        enqueue=True # Async safe
    )

configure_logging()
