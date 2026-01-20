# Prediction Approach: Booking Confirmation Probability

## Overview
The Prediction Service estimates the likelihood of a booking being "Confirmed" (indicating high demand or high value) based on trip parameters. This helps in dynamic pricing or inventory management (mock implementation).

## Model Choice
*   **Algorithm**: Random Forest Classifier (`sklearn.ensemble.RandomForestClassifier`).
*   **Reasoning**: Robust to outliers, handles non-linear relationships well, and provides `predict_proba` for probability scores.

## Feature Engineering
The model is trained on synthetic data with the following features:
1.  **`days_before_travel`**: Number of days between booking/query and travel date. (Closer dates -> Higher urgency).
2.  **`is_weekend`**: Boolean (1 for Sat/Sun). Weekends typically have higher demand.
3.  **`segment_length`**: Number of stops covered (e.g., Ahd->Mum is 4 segments). Longer trips potentially have higher commitment.
4.  **`current_bus_occupancy`**: Mock feature representing how full the bus is (0.0 to 1.0).

## API Output
The `/predict` endpoint returns:
*   `confirmation_probability`: 0-100% score.
*   `demand_level`: High (>75%), Medium (>40%), Low (<40%).
