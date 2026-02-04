@echo off
REM Provider Verification Dashboard - Quick Start Script
REM Windows PowerShell version

echo.
echo ========================================
echo Provider Verification Dashboard
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)

echo [INFO] Python found
python --version
echo.

REM Check if requirements are installed
echo [INFO] Checking dependencies...
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
) else (
    echo [INFO] Dependencies already installed
)
echo.

REM Check for .env file
if not exist .env (
    echo [WARNING] .env file not found
    echo [INFO] Using development mode with default settings
    echo [INFO] For production, copy .env.example to .env and configure
    echo.
)

echo ========================================
echo Starting Flask Application...
echo ========================================
echo.
echo Access the dashboard at:
echo   http://localhost:8080
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the application
python app.py

pause
