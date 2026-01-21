from fastapi import APIRouter, HTTPException, Query
from typing import List
from datetime import date
from pydantic import UUID4
from booking_service.schemas import Station, Seat, Meal, BookingRequest, BookingResponse
from booking_service.services.booking_logic import BookingService
from common.logger import logger
router = APIRouter()

@router.get("/stations", response_model=List[Station])
def get_stations():
    logger.debug("Fetching stations")
    return BookingService.get_stations()

@router.get("/meals", response_model=List[Meal])
def get_meals():
    logger.debug("Fetching meals")
    return BookingService.get_meals()

@router.get("/bookings", response_model=List[BookingResponse])
def get_bookings():
    bookings_data = BookingService.get_bookings()
    
    # Map raw DB data to Pydantic model
    return [
        BookingResponse(
            booking_id=b['id'],
            status=b['status'],
            message="Retrieved",
            total_amount=0.0 # Placeholder
        ) for b in bookings_data
    ]
    
@router.get("/seats", response_model=List[Seat])
def get_seats(
    from_station: UUID4, 
    to_station: UUID4, 
    travel_date: date
):
    try:
        logger.info(f"Checking seats: {from_station} -> {to_station} on {travel_date}")
        return BookingService.get_available_seats(from_station, to_station, travel_date)
    except Exception as e:
        logger.error(f"Error fetching seats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/book", response_model=BookingResponse)
def create_booking(booking: BookingRequest):
    try:
        return BookingService.create_booking(booking)
    except ValueError as e:
        if "available" in str(e):
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cancel/{booking_id}")
def cancel_booking(booking_id: UUID4):
    try:
        BookingService.cancel_booking(booking_id)
        return {"message": "Booking cancelled successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bookings", response_model=List[BookingResponse]) # Adjust schema if needed
def get_all_bookings():
    """
    Fetch all bookings for the 'My Bookings' page.
    Note: In a real app, this would filter by the logged-in User ID.
    """
    try:
        data = BookingService.get_bookings()
        return [
            BookingResponse(
                booking_id=item['id'],
                status=item['status'],
                message="Retrieved",
                total_amount=0.0 # Calculate real amount if you have price logic
            ) for item in data
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))