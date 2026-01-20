from fastapi import FastAPI
from booking_service.routers import bookings
from booking_service.core.logger import logger

app = FastAPI(title="Sleeper Bus Booking Service")

@app.on_event("startup")
async def startup_event():
    logger.info("Booking Service Starting...")

# Include Routers
app.include_router(bookings.router)

@app.get("/")
def read_root():
    logger.debug("Health check probe")
    return {"status": "Booking Service Running", "version": "1.0.0"}
