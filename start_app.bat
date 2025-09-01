@echo off
echo 🏥 Risk Stratification Web Application - Quick Start
echo ==================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed
echo.

REM Check if model exists
if not exist "models\risk_model.pkl" (
    echo 🤖 Training ML model...
    python train_model.py
    if errorlevel 1 (
        echo ❌ Failed to train model
        pause
        exit /b 1
    )
    echo ✅ Model trained successfully
) else (
    echo ✅ ML model found
)

echo.
echo 🚀 Starting application...
echo 📊 Dashboard: http://localhost:5000
echo 🛑 Press Ctrl+C to stop
echo.

REM Start the application
python app.py

pause
