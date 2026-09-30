@echo off
title Customer Complaint NLP System
cd /d "%~dp0"

echo ======================================================================
echo   CUSTOMER COMPLAINT CLASSIFICATION & PRIORITY DETECTION SYSTEM
echo   BE Semester 7 NLP Mini-Project
echo ======================================================================
echo.
echo [1/2] Opening web browser at http://127.0.0.1:5000/ ...
timeout /t 2 /nobreak >nul
start http://127.0.0.1:5000/

echo [2/2] Starting Flask server...
echo.
echo * Server is running! Press Ctrl+C in this window to stop it.
echo.
".venv\Scripts\python.exe" app.py

pause
