#!/bin/bash
# Provider Verification Dashboard - Quick Start Script
# Mac/Linux version

echo ""
echo "========================================"
echo "Provider Verification Dashboard"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.10+ from https://www.python.org/"
    exit 1
fi

echo "[INFO] Python found"
python3 --version
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[INFO] Creating virtual environment..."
    python3 -m venv venv
    echo "[INFO] Virtual environment created"
fi

# Activate virtual environment
echo "[INFO] Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
echo "[INFO] Checking dependencies..."
if ! python -c "import flask" &> /dev/null; then
    echo "[INFO] Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install dependencies"
        exit 1
    fi
else
    echo "[INFO] Dependencies already installed"
fi
echo ""

# Check for .env file
if [ ! -f .env ]; then
    echo "[WARNING] .env file not found"
    echo "[INFO] Using development mode with default settings"
    echo "[INFO] For production, copy .env.example to .env and configure"
    echo ""
fi

echo "========================================"
echo "Starting Flask Application..."
echo "========================================"
echo ""
echo "Access the dashboard at:"
echo "  http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the application
python app.py
