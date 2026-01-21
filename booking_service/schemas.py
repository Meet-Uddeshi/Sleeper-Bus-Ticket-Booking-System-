from pydantic import BaseModel, UUID4, Field
from datetime import date
from typing import List, Optional

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
    passenger_name: str = Field(..., min_length=1, description="Name of the passenger")
    meal_ids: Optional[List[UUID4]] = []

class BookingResponse(BaseModel):
    booking_id: UUID4
    status: str
    message: str
    total_amount: float