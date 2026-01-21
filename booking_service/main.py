from fastapi import FastAPI
from booking_service.routers import bookings
from common.logger import logger

app = FastAPI(title="Sleeper Bus Booking Service")

@app.on_event("startup")
async def startup_event():
    logger.info("Booking Service Starting...")

# Include Routers
app.include_router(bookings.router, prefix="/api/v1", tags=["bookings"])

@app.get("/")
def read_root():
    logger.debug("Health check probe")
    return {"status": "Booking Service Running", "version": "1.0.0"}

@app.on_event("startup")
def print_routes():
    import logging
    logger = logging.getLogger("uvicorn")
    logger.info("----------- REGISTERED ROUTES -----------")
    for route in app.routes:
        logger.info(f"Path: {route.path} | Name: {route.name}")
    logger.info("-----------------------------------------")