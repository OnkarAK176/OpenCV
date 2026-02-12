#!/bin/bash

# Traffic Violation Detection System - Quick Start Script for Unix/Linux/macOS

clear

echo "========================================================"
echo "  Traffic Violation Detection System - Quick Start"
echo "========================================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Display Python version
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "backend/venv" ]; then
    echo ""
    echo "Creating Python virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
fi

# Activate virtual environment
echo "Activating virtual environment..."
source backend/venv/bin/activate

# Install dependencies
echo ""
echo "Installing Python dependencies..."
echo "This may take a few minutes on first run..."
echo ""

cd backend
pip install -q -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed successfully"
echo ""
echo "========================================================"
echo "  Starting Traffic Violation Detection System"
echo "========================================================"
echo ""

# Start backend
echo "Starting Backend Server on port 5000..."
python app.py &
BACKEND_PID=$!

# Go back to root directory
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting Frontend Server on port 3000..."
cd frontend
python3 -m http.server 3000 &
FRONTEND_PID=$!

cd ..

echo ""
echo "========================================================"
echo "  System Started Successfully!"
echo "========================================================"
echo ""
echo "Backend:  http://localhost:5000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Opening frontend in browser..."

# Attempt to open browser
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3000
elif command -v open &> /dev/null; then
    open http://localhost:3000
fi

echo ""
echo "Press Ctrl+C to stop the servers"
echo ""

# Wait for user interrupt
wait
