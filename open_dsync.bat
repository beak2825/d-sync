@echo off
REM D-Sync Web Interface Launcher for Windows
REM This script opens the D-Sync dashboard in Chrome

echo.
echo ======================================
echo   D-Sync Web Interface Launcher
echo ======================================
echo.
echo Starting d-sync web server...
echo.
echo The dashboard will open in Chrome.
echo Access it at: http://localhost:5000
echo.
echo Press Ctrl+C in this window to stop.
echo.

python d_sync_web.py

pause
