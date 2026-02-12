param(
    [string]$Component = "both"
)

$projectRoot = "e:\Desktop\proj\traffic_violation_detection"

if ($Component -eq "backend" -or $Component -eq "both") {
    Write-Host "===== Starting Backend =====" -ForegroundColor Cyan
    Push-Location "$projectRoot\backend"
    python app.py
    Pop-Location
}

if ($Component -eq "frontend" -or $Component -eq "both") {
    Start-Sleep -Seconds 2
    Write-Host "===== Starting Frontend =====" -ForegroundColor Cyan
    Push-Location "$projectRoot\frontend"
    python -m http.server 3000
    Pop-Location
}
