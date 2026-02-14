#!/bin/bash

# 4-Panel Manga Generator Startup Script

echo "Starting 4-Panel Manga Generator..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and configure your API key."
    echo "  cp .env.example .env"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create required directories
mkdir -p static/layout_refs
mkdir -p static/char_refs
mkdir -p static/outputs

# Start the server
echo "Starting FastAPI server..."
echo "Access the application at: http://localhost:8000/static/index.html"
python main.py
