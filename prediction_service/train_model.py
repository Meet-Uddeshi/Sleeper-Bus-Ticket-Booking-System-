import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import random

def generate_mock_data(n_samples=1000):
    """
    Generates synthetic data for bus booking demand.
    Features: days_before_travel, is_weekend, segment_length, occupancy
    Target: is_confirmed (0 or 1)
    """
    data = []
    for _ in range(n_samples):
        days_before = random.randint(0, 30)
        is_weekend = random.choice([0, 1])
        segment_length = random.randint(1, 4) # Stations 1 to 5, max segment 4
        occupancy = random.uniform(0, 1.0) # 0 to 100% full
        
        # Mock Logic for target (Probability of confirmation/high demand)
        # Closer to date + weekend + long segment -> Higher chance of confirmation being needed/high demand
        score = (30 - days_before) * 2 + (is_weekend * 20) + (segment_length * 10) + (occupancy * 10)
        # Add some noise
        score += random.randint(-10, 10)
        
        is_confirmed = 1 if score > 60 else 0
        
        data.append([days_before, is_weekend, segment_length, occupancy, is_confirmed])
        
    columns = ['days_before_travel', 'is_weekend', 'segment_length', 'current_bus_occupancy', 'is_confirmed']
    return pd.DataFrame(data, columns=columns)

def train_and_save():
    print("Generating mock data...")
    df = generate_mock_data()
    
    X = df.drop('is_confirmed', axis=1)
    y = df['is_confirmed']
    
    print("Training Random Forest model...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y)
    
    # Save the model
    joblib.dump(clf, 'model.pkl')
    print("Model saved to model.pkl")

if __name__ == "__main__":
    train_and_save()
