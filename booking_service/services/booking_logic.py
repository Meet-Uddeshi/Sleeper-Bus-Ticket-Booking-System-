from datetime import date
from typing import List, Optional
from pydantic import UUID4
from booking_service.database import supabase
from booking_service.schemas import Station, Seat, Meal, BookingRequest, BookingResponse
from common.logger import logger

class BookingService:
    @staticmethod
    def get_stations() -> List[Station]:
        response = supabase.table("stations").select("*").order("sequence_order").execute()
        return response.data

    @staticmethod
    def get_available_seats(from_station: UUID4, to_station: UUID4, travel_date: date) -> List[Seat]:
        """
        Fetches available seats using the Postgres RPC function 'get_available_seats'.
        """
        # --- FIXED PARAMETERS (Sends 3 args now) ---
        params = {
            "req_start_station_id": str(from_station),
            "req_end_station_id": str(to_station),
            "req_travel_date": travel_date.isoformat()
        }
        
        try:
            print(f"DEBUG: Calling 'get_available_seats' with params: {params}")
            response = supabase.rpc("get_available_seats", params).execute()
            
            seats = []
            for item in response.data:
                seats.append(Seat(
                    id=item.get('id') or item.get('seat_id'),
                    seat_number=item.get('seat_number'),
                    type=item.get('type') or item.get('seat_type')
                ))
            return seats
            
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            return []

    @staticmethod
    def get_meals():
        try:
            response = supabase.table("meals").select("*").execute()
            if not response.data:
                # Fallback if table is empty or missing
                return [
                    {"id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "name": "Veg Thali", "price": 150.0, "type": "veg"},
                    {"id": "b1eebc99-9c0b-4ef8-bb6d-6bb9bd380a22", "name": "Chicken Biryani", "price": 250.0, "type": "non-veg"}
                ]
            return response.data
        except Exception as e:
            logger.warning(f"Could not fetch meals ({e}). Returning mock data.")
            return [
                {"id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "name": "Veg Thali", "price": 150.0, "type": "veg"},
                {"id": "b1eebc99-9c0b-4ef8-bb6d-6bb9bd380a22", "name": "Chicken Biryani", "price": 250.0, "type": "non-veg"}
            ]

    @staticmethod
    def create_booking(booking: BookingRequest) -> BookingResponse:
        try:
            # 1. Check Availability
            available_seats = BookingService.get_available_seats(
                booking.start_station_id, 
                booking.end_station_id, 
                booking.travel_date
            )
            
            # Verify the specific seat is still in the available list
            is_available = any(str(s.id) == str(booking.seat_id) for s in available_seats)
            
            if not is_available:
                # This raises a 500 error if not handled, so we log it
                print(f"DEBUG: Seat {booking.seat_id} is NOT available.")
                raise ValueError(f"Seat {booking.seat_id} is already booked or unavailable.")
            
            # 2. Prepare Booking Data
            booking_data = {
                "seat_id": str(booking.seat_id),
                "start_station_id": str(booking.start_station_id),
                "end_station_id": str(booking.end_station_id),
                "travel_date": booking.travel_date.isoformat(),
                "status": "CONFIRMED",
                # ✅ UNCOMMENTED and Fixed:
                "passenger_name": booking.passenger_name 
            }
            
            print(f"DEBUG: Inserting Booking: {booking_data}")

            # 3. Insert into Database
            res = supabase.table("bookings").insert(booking_data).execute()
            
            if not res.data:
                 raise Exception("Database insert returned no data")
            
            new_booking_id = res.data[0]['id']
            
            # 4. Insert Meals (Optional)
            if booking.meal_ids:
                meal_inserts = [{"booking_id": new_booking_id, "meal_id": str(mid)} for mid in booking.meal_ids]
                supabase.table("booking_meals").insert(meal_inserts).execute()
                
            return BookingResponse(
                booking_id=new_booking_id, 
                status="CONFIRMED", 
                message="Booking successful",
                total_amount=0.0
            )

        except Exception as e:
            # ✅ CATCH & PRINT THE REAL ERROR
            print(f"CRITICAL BOOKING ERROR: {str(e)}")
            raise e # Re-raise so FastAPI returns 500, but now we see why in the logs
    
    @staticmethod
    def get_bookings():
        """
        Fetches all bookings from the database.
        """
        try:
            # Order by created_at descending (newest first)
            response = supabase.table("bookings").select("*").order("created_at", desc=True).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching bookings: {e}")
            return []