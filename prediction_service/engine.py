import joblib
import pandas as pd
import os
from datetime import date

from core.logger import logger

class PredictionEngine:
    def __init__(self, model_path: str = "model.pkl"):
        self.model_path = model_path
        self.model = None

    def load_model(self):
        """Loads the model from disk if available."""
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            logger.info(f"Model loaded from {self.model_path}")
        else:
            logger.warning(f"{self.model_path} not found. Prediction service will fail until trained.")

    def predict(self, travel_date: date, start_station_order: int, end_station_order: int):
        """
        Runs the prediction logic.
        """
        if not self.model:
            raise ValueError("Model not loaded")

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
        try:
            prob = self.model.predict_proba(features)[0][1] # Probability of class 1
        except Exception as e:
             raise ValueError(f"Prediction failed: {e}")
        
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
