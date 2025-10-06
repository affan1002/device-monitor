#!/bin/bash
# Device Monitor Agent - Quick Setup Script for Linux/Mac
# Run this script on the new computer after copying the agent folder

echo "========================================"
echo "Device Monitor Agent - Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo "Please install Python 3 first"
    exit 1
fi

echo "[1/5] Python detected: $(python3 --version)"
echo ""

# Create virtual environment
echo "[2/5] Creating virtual environment..."
python3 -m venv .venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "[3/5] Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "[4/5] Installing dependencies..."
pip install -r requirements.txt
pip install pytz

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

# Setup configuration
echo "[5/5] Configuration setup..."
echo ""

if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Edit .env file and set:"
    echo "  - SERVER_HOST to your server's IP address"
    echo "  - AGENT_ID to a unique name for this device"
    echo ""
else
    echo ".env file already exists"
fi

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file and configure:"
echo "   - SERVER_HOST (your server's IP)"
echo "   - AGENT_ID (unique device name)"
echo ""
echo "2. Make sure the server is running"
echo ""
echo "3. Run the agent with:"
echo "   source .venv/bin/activate"
echo "   python agent/main.py"
echo ""
echo "========================================"
