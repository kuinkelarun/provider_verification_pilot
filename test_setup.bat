@echo off
REM Test Script for Provider Verification Dashboard v2.0

echo ========================================
echo Provider Verification Dashboard v2.0
echo Testing Pre-Processed Data Display
echo ========================================
echo.

echo [1/5] Checking Python installation...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found! Please install Python 3.8+
    pause
    exit /b 1
)
echo OK
echo.

echo [2/5] Checking required dependencies...
pip show flask >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Flask not installed. Installing dependencies...
    pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
) else (
    echo OK - Dependencies already installed
)
echo.

echo [3/5] Checking data storage directory...
if not exist "data_storage" (
    echo Creating data_storage directory...
    mkdir data_storage
    echo Created: data_storage\
) else (
    echo OK - data_storage\ exists
)
echo.

echo [4/5] Checking uploads directory...
if not exist "uploads" (
    echo Creating uploads directory...
    mkdir uploads
    echo Created: uploads\
) else (
    echo OK - uploads\ exists
)
echo.

echo [5/5] Verifying sample data...
if exist "static\sample_verification_results.csv" (
    echo OK - Sample file exists
) else (
    if exist "sample_data\sample_verification_results.csv" (
        echo Copying sample file to static folder...
        copy "sample_data\sample_verification_results.csv" "static\sample_verification_results.csv" >nul
        echo OK - Sample file copied
    ) else (
        echo WARNING: Sample file not found
    )
)
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the dashboard:
echo   python app.py
echo.
echo Then open your browser to:
echo   http://localhost:5000
echo.
echo Sample file available at:
echo   static\sample_verification_results.csv
echo.
echo Documentation:
echo   README_V2.md - Overview
echo   QUICKSTART_V2.md - Quick start guide
echo   ARCHITECTURE_CHANGES.md - Technical details
echo.
pause
