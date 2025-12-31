@echo off
REM MarkDown OCR - LLM Connection Test Wrapper (Windows)
REM This script provides a convenient way to test your LLM connection

echo ==========================================
echo MarkDown OCR - LLM Connection Test
echo ==========================================
echo.

REM Change to backend directory
cd /d "%~dp0backend"

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements are installed
if not exist "venv\.installed" (
    echo Installing dependencies...
    pip install -q -r requirements.txt
    echo. > venv\.installed
    echo Dependencies installed
    echo.
)

REM Run the test script
echo Running LLM connection test...
echo.
python test_llm_connection.py

REM Deactivate virtual environment
call venv\Scripts\deactivate.bat

echo.
echo Test complete!
pause
