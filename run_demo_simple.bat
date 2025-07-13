@echo off
echo Starting Demo Dashboard...
echo.

REM Kill any existing Python processes
taskkill /f /im python.exe >nul 2>&1

REM Wait a moment
timeout /t 2 /nobreak >nul

REM Run the demo
cd demo
python run_demo.py

pause 