@echo off
REM Start frontend web server

cd ..\frontend
python -m http.server 3000
