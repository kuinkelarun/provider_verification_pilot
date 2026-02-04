@echo off
REM Quick Start Script for Provider Verification Dashboard

echo.
echo ===============================================
echo  Provider Verification Dashboard v2.0
echo  Quick Start
echo ===============================================
echo.

REM Check if dependencies are installed
pip show flask >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [Step 1/2] Installing dependencies...
    pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERROR: Failed to install dependencies
        echo Please check your internet connection and try again.
        pause
        exit /b 1
    )
    echo Dependencies installed successfully!
    echo.
) else (
    echo [Step 1/2] Dependencies already installed ✓
    echo.
)

echo [Step 2/2] Starting Flask application...
echo.
echo -----------------------------------------------
echo  Server will start at: http://localhost:5000
echo  Press Ctrl+C to stop the server
echo -----------------------------------------------
echo.

python app.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to start application
    echo Check the error messages above
    pause
    exit /b 1
)
