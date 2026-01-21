# Prediction Approach: Demand Forecasting Engine

## 1. Overview
The **Prediction Service** is designed to estimate the **likelihood of a booking confirmation** and categorize the **demand level** (High, Medium, Low) for a given bus route and date. 

To ensure consistency during development and demonstrations without requiring a live trained model pipeline, we utilize a **Deterministic Logic Engine** that simulates the behavior of a trained **Random Forest Regressor**.

---

## 2. Prediction Logic (Deterministic Engine)

The core logic transforms input parameters into a consistent "random" probability score using SHA-256 hashing. This ensures that:
- **Consistency**: Inputting the same *Route + Date* always yields the exact same percentage.
- **Realism**: The score fluctuates based on logical business rules (weekends are busier, long trips are more committed).

### Key Factors (Weights)
| Factor | Condition | Impact on Score | Rationale |
| :--- | :--- | :--- | :--- |
| **Base Score** | N/A | `60.0` | Initial probability intercept. |
| **Weekend** | Friday or Sunday | `+15.0` | Peak travel days for sleepers. |
| **Weekend** | Saturday | `+5.0` | Moderate travel day. |
| **Weekday** | Mon-Thu | `-5.0` | Lower demand on workdays. |
| **Distance** | `(End - Start)` | `+3.0` per station | Longer trips have lower cancellation rates. |
| **Seasonality** | Dec, Jan, May | `+10.0` | Holiday/Vacation seasons. |

### Deterministic Noise
To simulate natural variance (e.g., specific dates just happening to be busier), we apply "noise" (`-5.0` to `+5.0`) derived from the **hash** of the input string:
`"{start_station}-{end_station}-{travel_date}"`

---

## 3. Model Choice (Simulated)

While the current specific implementation is rule-based for stability, the architecture is designed to host a **Random Forest Classifier/Regressor**.

- **Why Random Forest?**
  - Handles non-linear relationships well (e.g., demand doesn't increase linearly with days-before-travel).
  - Robust against overfitting with small datasets.
  - interpretability (feature importance).

---

## 4. Mock Dataset

The logic simulates a dataset with the following schema:

| Feature | Type | Description |
| :--- | :--- | :--- |
| `travel_date` | Date | The intended date of journey. |
| `start_station_id` | Int | Sequence order of departure. |
| `end_station_id` | Int | Sequence order of arrival. |
| `days_before_travel` | Int | `Travel Date - Booking Date`. |
| **Target** | Float | **Confirmation Probability (0.0 - 1.0)** |

---

## 5. Booking Probability Output (%)

The service outputs a JSON response with two key metrics:

### **1. Confirmation Probability**
A percentage value between **10%** and **98.5%**. 
- Formula: `Clamp(Base + Weights + Noise, 10, 98.5)`

### **2. Demand Level**
Categorical classification based on the probability score.

| Probability Score | Demand Level | UX Indication |
| :--- | :--- | :--- |
| **> 80%** | **High** | 🔥 Red Warning ("Book fast!") |
| **55% - 80%** | **Medium** | ⚠️ Yellow Info ("Moderate demand") |
| **< 55%** | **Low** | ✅ Green Success ("Good availability") |
