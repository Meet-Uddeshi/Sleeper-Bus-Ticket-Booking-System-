@echo off
setlocal

REM Check if virtual environment exists
if not exist ".venv\" (
    echo [ERROR] Virtual environment (.venv) not found!
    echo Please create it first.
    pause
    exit /b 1
)

echo [INFO] Detected .venv directory.
echo.

echo [STARTING] Booking Service (Port 8000)...
start "Booking Service" cmd /k "call .venv\Scripts\activate & uvicorn booking_service.main:app --reload --port 8000"
timeout /t 3 /nobreak
echo.

echo [STARTING] Prediction Service (Port 8001)...
start "Prediction Service" cmd /k "call .venv\Scripts\activate & uvicorn prediction_service.main:app --reload --port 8001"
timeout /t 3 /nobreak
echo.

echo [STARTING] Frontend (Streamlit)...
start "Frontend" cmd /k "call .venv\Scripts\activate & streamlit run frontend/app.py"
echo.

echo [SUCCESS] All services launched in separate windows.
echo Keep this window open to monitor logic or close it if done.
pause
