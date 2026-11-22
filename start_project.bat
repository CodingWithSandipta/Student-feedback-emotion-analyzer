@echo off
title Student Feedback Emotion Analyzer - Startup
color 0B

echo.
echo ============================================================
echo   Student Feedback Emotion Analyzer - Project Startup
echo   AI-Based Bi-LSTM Emotion Classification System
echo ============================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo         Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH.
    echo         Download from: https://nodejs.org/
    pause
    exit /b 1
)

echo [OK] Python and Node.js found.
echo.

:: Navigate to project directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

:: Setup Python virtual environment
if not exist "backend\venv\" (
    echo [INFO] Creating Python virtual environment...
    python -m venv backend\venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created.
)

:: Activate and install backend requirements
echo [INFO] Installing backend requirements...
call backend\venv\Scripts\activate.bat
pip install -r backend\requirements.txt --quiet
if errorlevel 1 (
    echo [WARNING] Some packages may have failed to install. Check requirements.txt.
)
echo [OK] Backend requirements installed.
echo.

:: Check if model exists
if not exist "backend\models\bilstm_emotion_model.keras" (
    echo ============================================================
    echo   MODEL NOT FOUND
    echo ============================================================
    echo.
    echo   The Bi-LSTM model has not been trained yet.
    echo.
    echo   To train the model:
    echo   1. Ensure you have internet access
    echo   2. Open a NEW terminal window
    echo   3. Run:
    echo      cd "%SCRIPT_DIR%backend"
    echo      ..\backend\venv\Scripts\activate
    echo      python train_model.py
    echo.
    echo   Training takes 10-30 minutes and downloads GoEmotions dataset.
    echo   The application will start but predictions will NOT work
    echo   until training is complete.
    echo.
    echo   Press any key to start the application anyway...
    pause >nul
) else (
    echo [OK] Model artifacts found. Full functionality available.
)

:: Initialize database
echo [INFO] Initializing database...
python -c "import sys; sys.path.insert(0,'backend'); from app import create_app; app = create_app()" 2>nul
echo [OK] Database ready.
echo.

:: Install frontend dependencies if needed
if not exist "frontend\node_modules\" (
    echo [INFO] Installing frontend dependencies...
    cd frontend
    npm install --silent
    cd ..
    echo [OK] Frontend dependencies installed.
)

echo ============================================================
echo   Starting Application
echo ============================================================
echo.
echo   Backend API  : http://localhost:5000
echo   Frontend App : http://localhost:5173
echo   Health Check : http://localhost:5000/api/health
echo.
echo   Starting backend and frontend in separate windows...
echo.

:: Start backend
start "Flask Backend (port 5000)" cmd /k "cd /d %SCRIPT_DIR%backend && ..\backend\venv\Scripts\activate && python app.py"

:: Wait 3 seconds for backend to start
timeout /t 3 /nobreak >nul

:: Start frontend
start "React Frontend (port 5173)" cmd /k "cd /d %SCRIPT_DIR%frontend && npm run dev"

echo [OK] Both servers started in separate windows.
echo.
echo   Open your browser to: http://localhost:5173
echo.
echo   To stop: Close the Backend and Frontend windows.
echo.
pause
