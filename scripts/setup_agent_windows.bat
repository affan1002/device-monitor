@echo off
REM Device Monitor Agent - Quick Setup Script for Windows
REM Run this script on the new computer after copying the agent folder

echo ========================================
echo Device Monitor Agent - Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [1/5] Python detected
echo.

REM Create virtual environment
echo [2/5] Creating virtual environment...
python -m venv .venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo [3/5] Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install dependencies
echo [4/5] Installing dependencies...
pip install -r requirements.txt
pip install pytz

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Setup configuration
echo [5/5] Configuration setup...
echo.

if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo IMPORTANT: Edit .env file and set:
    echo   - SERVER_HOST to your server's IP address
    echo   - AGENT_ID to a unique name for this device
    echo.
) else (
    echo .env file already exists
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file and configure:
echo    - SERVER_HOST (your server's IP)
echo    - AGENT_ID (unique device name)
echo.
echo 2. Make sure the server is running
echo.
echo 3. Run the agent with:
echo    .venv\Scripts\activate
echo    python agent/main.py
echo.
echo ========================================
pause
