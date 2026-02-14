@echo off
REM 4-Panel Manga Generator Startup Script for Windows

echo Starting 4-Panel Manga Generator...

REM Check if .env file exists
if not exist .env (
    echo Error: .env file not found!
    echo Please copy .env.example to .env and configure your API key.
    echo   copy .env.example .env
    exit /b 1
)

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create required directories
if not exist static\layout_refs mkdir static\layout_refs
if not exist static\char_refs mkdir static\char_refs
if not exist static\outputs mkdir static\outputs

REM Start the server
echo Starting FastAPI server...
echo Access the application at: http://localhost:8000/static/index.html
python main.py
