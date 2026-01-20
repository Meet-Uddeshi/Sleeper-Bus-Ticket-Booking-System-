from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from datetime import date
from engine import PredictionEngine
from core.logger import logger

app = FastAPI(title="Demand Prediction Service")

# Global Instance (Singleton-ish pattern for this simple app)
prediction_engine = PredictionEngine()

@app.on_event("startup")
def startup_event():
    logger.info("Prediction Service Starting...")
    prediction_engine.load_model()

class PredictionRequest(BaseModel):
    travel_date: date
    start_station_order: int 
    end_station_order: int

class PredictionResponse(BaseModel):
    confirmation_probability: float
    demand_level: str

@app.post("/predict", response_model=PredictionResponse)
def predict_demand(request: PredictionRequest):
    try:
        result = prediction_engine.predict(
            travel_date=request.travel_date,
            start_station_order=request.start_station_order,
            end_station_order=request.end_station_order
        )
        return result
    except ValueError as e:
        if "Model not loaded" in str(e):
            raise HTTPException(status_code=503, detail="Prediction model is not available.")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
