from datetime import date
from typing import List, Optional
from pydantic import UUID4
from booking_service.database import supabase
from booking_service.schemas import Station, Seat, Meal, BookingRequest, BookingResponse
from booking_service.core.logger import logger

class BookingService:
    @staticmethod
    def get_stations() -> List[Station]:
        response = supabase.table("stations").select("*").order("sequence_order").execute()
        return response.data

    @staticmethod
    def get_meals() -> List[Meal]:
        response = supabase.table("meals").select("*").execute()
        return response.data

    @staticmethod
    def get_bookings():
        response = supabase.table("bookings").select("*").order("created_at", desc=True).execute()
        return response.data

    @staticmethod
    def get_available_seats(from_station: UUID4, to_station: UUID4, travel_date: date) -> List[Seat]:
        params = {
            "p_start_station_id": str(from_station),
            "p_end_station_id": str(to_station),
            "p_travel_date": travel_date.isoformat()
        }
        try:
            response = supabase.rpc("check_availability", params).execute()
            seats = []
            for item in response.data:
                seats.append(Seat(
                    id=item['seat_id'],
                    seat_number=item['seat_number'],
                    type=item['seat_type']
                ))
            return seats
        except Exception as e:
            print(f"Error checking availability: {e}")
            raise e

    @staticmethod
    def create_booking(booking: BookingRequest) -> BookingResponse:
        # Atomic(ish) check
        available_seats = BookingService.get_available_seats(booking.start_station_id, booking.end_station_id, booking.travel_date)
        is_available = any(str(s.id) == str(booking.seat_id) for s in available_seats)
        
        if not is_available:
            raise ValueError("Seat is no longer available.")
        
        # Insert Booking
        booking_data = {
            "seat_id": str(booking.seat_id),
            "start_station_id": str(booking.start_station_id),
            "end_station_id": str(booking.end_station_id),
            "travel_date": booking.travel_date.isoformat(),
            "status": "CONFIRMED"
        }
        res = supabase.table("bookings").insert(booking_data).execute()
        if not res.data:
             raise Exception("Failed to create booking")
        
        new_booking_id = res.data[0]['id']
        
        # Add Meals
        if booking.meal_ids:
            meal_inserts = [{"booking_id": new_booking_id, "meal_id": str(mid)} for mid in booking.meal_ids]
            supabase.table("booking_meals").insert(meal_inserts).execute()
            
        return BookingResponse(
            booking_id=new_booking_id, 
            status="CONFIRMED", 
            message="Booking successful",
            total_amount=0.0
        )

    @staticmethod
    def cancel_booking(booking_id: UUID4):
        res = supabase.table("bookings").update({"status": "CANCELLED"}).eq("id", str(booking_id)).execute()
        if not res.data:
            raise ValueError("Booking not found")
        return True
