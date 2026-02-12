# PowerShell script to start both servers properly

Write-Host "Starting Traffic Violation Detection System..." -ForegroundColor Green
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
$venvPath = ".\backend\venv_new\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    & $venvPath
} else {
    Write-Host "Virtual environment not found. Creating one..." -ForegroundColor Yellow
    cd backend
    python -m venv venv_new
    & .\venv_new\Scripts\Activate.ps1
    cd ..
}

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
cd backend
pip install -r requirements.txt
cd ..

Write-Host ""
Write-Host "Starting backend server..." -ForegroundColor Cyan
cd backend
start-process powershell -ArgumentList "-NoExit", "-Command", "python app.py"
cd ..

Write-Host "Waiting 3 seconds for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "Starting frontend server..." -ForegroundColor Cyan
cd frontend
start-process powershell -ArgumentList "-NoExit", "-Command", "python -m http.server 3000"
cd ..

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "System Started Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "Backend:  http://localhost:5000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Opening frontend in browser..." -ForegroundColor Yellow
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "Press Enter to exit..." -ForegroundColor Yellow
Read-Host
