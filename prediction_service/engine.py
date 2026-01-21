import joblib
import pandas as pd
import os
from datetime import date
from common.logger import logger
import random

class PredictionEngine:
    def __init__(self, model_path: str = "model.pkl"):
        self.model_path = model_path
        self.model = None

    @staticmethod
    def load_model():
        # Mock loading - doing nothing is fine for now
        print("Mock Model 'loaded' successfully.")

    def predict(self, travel_date: date, start_station_order: int, end_station_order: int):
        """
        Runs the prediction logic.
        """
        if not self.model:
            # For now, allow running without model if we use the static method logic primarily
            # But the user code calls predict().
            # Let's fallback to predict_confirmation logic if model is missing, or raise.
            # The original code raised ValueError.
            # But the user changed load_model to do nothing.
            # So self.model will be None.
            # If self.model is None, this method will raise "Model not loaded".
            # This seems to be a bug introduced by the user mocking load_model but not updating predict.
            # I should fix this to use the new logic if model is missing.
            pass

        # Feature Engineering (Same logic as before, now encapsulated)
        today = date.today()
        days_before = (travel_date - today).days
        if days_before < 0: days_before = 0 
        
        is_weekend = 1 if travel_date.weekday() >= 5 else 0
        
        segment_length = end_station_order - start_station_order
        if segment_length <= 0:
            segment_length = 1 
            
        occupancy = 0.5 # Mock value
        
        features = pd.DataFrame([[days_before, is_weekend, segment_length, occupancy]], 
                                columns=['days_before_travel', 'is_weekend', 'segment_length', 'current_bus_occupancy'])
        
        # Predict
        if self.model:
            try:
                prob = self.model.predict_proba(features)[0][1] # Probability of class 1
            except Exception as e:
                 raise ValueError(f"Prediction failed: {e}")
        else:
            # Fallback to new math logic if model is not loaded (mock mode)
            prob = PredictionEngine.predict_confirmation(start_station_order, end_station_order, travel_date.weekday()) / 100.0

        prob_percentage = round(prob * 100, 2)
        
        demand_level = "Low"
        if prob_percentage > 75:
            demand_level = "High"
        elif prob_percentage > 40:
            demand_level = "Medium"
            
        return {
            "confirmation_probability": prob_percentage,
            "demand_level": demand_level
        }

    @staticmethod
    def predict_confirmation(start_seq: int, end_seq: int, day_of_week: int) -> float:
        """
        Pure math logic, no file loading required.
        """
        base_prob = 75.0
        
        # Logic: Longer distance = Higher commitment
        distance_factor = (end_seq - start_seq) * 3 
        
        # Logic: Weekend (5=Sat, 6=Sun) is busier
        weekend_factor = 10 if day_of_week in [5, 6] else 0
        
        # Add randomness
        probability = base_prob + distance_factor + weekend_factor + random.uniform(-5, 5)
        
        # Clamp between 0 and 100
        return min(max(probability, 5.0), 99.0)