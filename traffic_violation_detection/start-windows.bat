@echo off
REM Traffic Violation Detection System - Quick Start Script for Windows

echo.
echo ========================================================
echo  Traffic Violation Detection System - Quick Start
echo ========================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in PATH
    echo Please download Python 3.8+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "backend\venv" (
    echo Creating Python virtual environment...
    cd backend
    python -m venv venv
    cd ..
)

REM Activate virtual environment
echo Activating virtual environment...
call backend\venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing Python dependencies...
echo This may take a few minutes...
cd backend
pip install -q -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo ✓ Dependencies installed successfully
echo.
echo ========================================================
echo  Starting Traffic Violation Detection System
echo ========================================================
echo.

REM Start backend in new window
echo Starting Backend Server on port 5000...
start cmd /k "cd backend && python app.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak

REM Start frontend
echo Starting Frontend Server on port 3000...
start cmd /k "cd frontend && python -m http.server 3000"

echo.
echo ========================================================
echo  System Started Successfully!
echo ========================================================
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Opening frontend in browser...
start http://localhost:3000
echo.
echo Press Ctrl+C in either terminal to stop the servers
echo.
pause
