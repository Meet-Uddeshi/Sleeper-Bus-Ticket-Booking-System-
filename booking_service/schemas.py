from pydantic import BaseModel, Field, UUID4
from typing import List, Optional
from datetime import date

class Station(BaseModel):
    id: UUID4
    name: str
    sequence_order: int

class Seat(BaseModel):
    id: UUID4
    seat_number: str
    type: str

class Meal(BaseModel):
    id: UUID4
    name: str
    price: float
    type: str

class BookingRequest(BaseModel):
    seat_id: UUID4
    start_station_id: UUID4
    end_station_id: UUID4
    travel_date: date
    meal_ids: List[UUID4] = []

class BookingResponse(BaseModel):
    booking_id: UUID4
    status: str
    message: str
    total_amount: Optional[float] = 0.0
