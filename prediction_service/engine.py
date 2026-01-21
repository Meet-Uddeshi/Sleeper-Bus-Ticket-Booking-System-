import hashlib
from datetime import date
from common.logger import logger

class PredictionEngine:
    def __init__(self, model_path: str = "model.pkl"):
        # We are using a simulated deterministic model, so we don't load a physical file.
        self.model_path = model_path

    @staticmethod
    def load_model():
        logger.info("Deterministic Random Forest Simulator loaded successfully.")

    def predict(self, travel_date: date, start_station_order: int, end_station_order: int) -> dict:
        """
        Main entry point for the API.
        Delegates to the deterministic logic engine.
        """
        # Convert date to string for consistency in hashing
        date_str = travel_date.isoformat()
        
        return self.calculate_deterministic_score(
            start_seq=start_station_order,
            end_seq=end_station_order,
            travel_date_str=date_str,
            travel_date_obj=travel_date
        )

    @staticmethod
    def calculate_deterministic_score(start_seq: int, end_seq: int, travel_date_str: str, travel_date_obj: date) -> dict:
        """
        Simulates a trained Random Forest Regressor with DETERMINISTIC output.
        
        The 'randomness' is derived from a SHA-256 hash of the inputs.
        This ensures that the same Date + Route ALWAYS produces the same result.
        """
        
        # 1. Feature Engineering
        day_of_week = travel_date_obj.weekday() # 0=Mon, 6=Sun
        month = travel_date_obj.month
        distance = abs(end_seq - start_seq)

        # 2. Base "Model" Weights (Simulating Learned Coefficients)
        # Start with a base probability (Intercept)
        score = 60.0

        # WEIGHT A: Weekends are busier (Fri=4, Sat=5, Sun=6)
        if day_of_week in [4, 6]: 
            score += 15.0  # High demand spike on Fri/Sun
        elif day_of_week == 5:
            score += 5.0   # Moderate on Saturday
        else:
            score -= 5.0   # Lower on weekdays

        # WEIGHT B: Long Distance trips are booked more seriously (Lower cancellation)
        score += (distance * 3.0) 

        # WEIGHT C: Seasonality (Peak months: Dec, Jan, May)
        if month in [12, 1, 5]:
            score += 10.0

        # 3. Deterministic Noise (The Core "Same Demand" Logic)
        # We create a unique signature string for this specific trip
        input_signature = f"{start_seq}-{end_seq}-{travel_date_str}"
        
        # Hash it to get a consistent "random" number
        hash_object = hashlib.sha256(input_signature.encode('utf-8'))
        hash_hex = hash_object.hexdigest()
        
        # Convert first 4 chars of hash to an integer to generate consistent noise (-5.0 to +5.0)
        hash_val = int(hash_hex[:4], 16) 
        deterministic_noise = (hash_val % 100) / 10.0 - 5.0
        
        final_score = score + deterministic_noise

        # 4. Clamping (Keep within realistic 10% - 98% range)
        final_score = min(max(final_score, 10.0), 98.5)

        # 5. Classification
        if final_score > 80:
            demand = "High"
        elif final_score > 55:
            demand = "Medium"
        else:
            demand = "Low"

        return {
            "confirmation_probability": round(final_score, 1),
            "demand_level": demand
        }