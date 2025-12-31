@echo off
REM MarkDown OCR Setup Verification Script (Windows)
REM This script verifies that your system is properly configured for PDF to Markdown conversion

setlocal enabledelayedexpansion

set PASSED=0
set FAILED=0
set WARNINGS=0

echo.
echo ================================================================
echo        MarkDown OCR v2.0 - Setup Verification
echo ================================================================
echo.

REM Function to print messages (using echo with formatting)
goto :main

:print_success
set /a PASSED+=1
echo [92m PASS [0m %~1
goto :eof

:print_error
set /a FAILED+=1
echo [91m FAIL [0m %~1
goto :eof

:print_warning
set /a WARNINGS+=1
echo [93m WARN [0m %~1
goto :eof

:print_info
echo [94m INFO [0m %~1
goto :eof

:main

echo ================================================================
echo 1. Checking Prerequisites
echo ================================================================

REM Check Python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    call :print_success "Python installed: !PYTHON_VERSION!"
) else (
    call :print_error "Python not found"
)

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f %%i in ('node --version') do set NODE_VERSION=%%i
    call :print_success "Node.js installed: !NODE_VERSION!"
) else (
    call :print_error "Node.js not found"
)

REM Check npm
npm --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f %%i in ('npm --version') do set NPM_VERSION=%%i
    call :print_success "npm installed: !NPM_VERSION!"
) else (
    call :print_error "npm not found"
)

REM Check Docker
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=3" %%i in ('docker --version') do set DOCKER_VERSION=%%i
    call :print_success "Docker installed: !DOCKER_VERSION!"
) else (
    call :print_warning "Docker not found (optional, but recommended)"
)

echo.
echo ================================================================
echo 2. Checking LLM Provider
echo ================================================================

REM Check Ollama
ollama --version >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "Ollama CLI found"

    REM Check if Ollama is running
    curl -s http://localhost:11434/api/tags >nul 2>&1
    if !errorlevel! equ 0 (
        call :print_success "Ollama server is running on port 11434"
        echo.
        call :print_info "Available Ollama models:"
        ollama list 2>nul
        echo.
    ) else (
        call :print_warning "Ollama server is not running"
        call :print_info "Start it with: ollama serve"
    )
) else (
    call :print_warning "Ollama not found"
    call :print_info "Install from: https://ollama.com/"
)

REM Check LM Studio
curl -s http://localhost:1234/v1/models >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "LM Studio server detected on port 1234"
) else (
    call :print_warning "LM Studio server not detected on port 1234"
    call :print_info "If using LM Studio, make sure the server is started"
)

echo.
echo ================================================================
echo 3. Checking Project Structure
echo ================================================================

REM Check backend
if exist "backend\" (
    call :print_success "Backend directory found"

    if exist "backend\requirements.txt" (
        call :print_success "Backend requirements.txt exists"
    ) else (
        call :print_error "Backend requirements.txt missing"
    )

    if exist "backend\app\main.py" (
        call :print_success "Backend main.py exists"
    ) else (
        call :print_error "Backend main.py missing"
    )
) else (
    call :print_error "Backend directory not found"
)

REM Check frontend
if exist "frontend\" (
    call :print_success "Frontend directory found"

    if exist "frontend\package.json" (
        call :print_success "Frontend package.json exists"
    ) else (
        call :print_error "Frontend package.json missing"
    )
) else (
    call :print_error "Frontend directory not found"
)

REM Check docker-compose
if exist "docker-compose.yml" (
    call :print_success "docker-compose.yml exists"
) else (
    call :print_warning "docker-compose.yml not found"
)

echo.
echo ================================================================
echo 4. Checking Python Dependencies
echo ================================================================

if exist "backend\venv\" (
    call :print_success "Python virtual environment found"
) else (
    call :print_warning "No virtual environment detected"
    call :print_info "Create one with: cd backend && python -m venv venv"
)

REM Try to check if required packages are installed
python -c "import fastapi" >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "FastAPI installed"
) else (
    call :print_warning "FastAPI not installed"
    call :print_info "Install with: pip install -r backend\requirements.txt"
)

python -c "import fitz" >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "PyMuPDF installed"
) else (
    call :print_warning "PyMuPDF not installed"
)

python -c "import PIL" >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "Pillow (PIL) installed - Vision support ready"
) else (
    call :print_warning "Pillow not installed - Required for vision model support"
    call :print_info "Install with: pip install Pillow"
)

python -c "import langchain_openai" >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "LangChain OpenAI installed"
) else (
    call :print_warning "LangChain OpenAI not installed"
)

echo.
echo ================================================================
echo 5. Checking Configuration
echo ================================================================

if exist "backend\.env" (
    call :print_success "Environment file (.env) found"
    echo.
    call :print_info "Current configuration:"

    findstr "USE_VISION_MODEL" backend\.env >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "tokens=2 delims==" %%i in ('findstr "USE_VISION_MODEL" backend\.env') do (
            if "%%i"=="true" (
                echo     [92m*[0m Vision Model: ENABLED
            ) else (
                echo     * Vision Model: DISABLED ^(text-only mode^)
            )
        )
    )

    findstr "VISION_MODEL" backend\.env >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "tokens=2 delims==" %%i in ('findstr "^VISION_MODEL=" backend\.env') do echo     * Vision Model: %%i
    )

    findstr "LLM_MODEL" backend\.env >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "tokens=2 delims==" %%i in ('findstr "^LLM_MODEL=" backend\.env') do echo     * Text Model: %%i
    )

    findstr "PDF_DPI" backend\.env >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "tokens=2 delims==" %%i in ('findstr "PDF_DPI" backend\.env') do echo     * PDF DPI: %%i
    )
    echo.
) else (
    call :print_warning "No .env file found (using defaults)"
    call :print_info "Copy env.template to .env to customize settings"
)

echo.
echo ================================================================
echo 6. Testing LLM Connection
echo ================================================================

if exist "backend\test_llm_connection.py" (
    call :print_info "Running LLM connection test..."
    echo.

    cd backend
    python test_llm_connection.py
    if !errorlevel! equ 0 (
        cd ..
        call :print_success "LLM connection test passed!"
    ) else (
        cd ..
        call :print_error "LLM connection test failed"
        call :print_info "Check the output above for troubleshooting steps"
    )
) else (
    call :print_warning "LLM test script not found"
)

echo.
echo ================================================================
echo Summary
echo ================================================================
echo.
echo [92m PASS:[0m !PASSED!
echo [93m WARN:[0m !WARNINGS!
echo [91m FAIL:[0m !FAILED!
echo.

if !FAILED! equ 0 (
    echo [92m================================================================[0m
    echo [92m  Setup Complete! You're ready to start converting!            [0m
    echo [92m================================================================[0m
    echo.
    echo Next steps:
    echo   1. Start the application:
    echo      [94mdocker-compose up --build[0m
    echo      OR
    echo      [94mcd backend ^&^& uvicorn app.main:app --reload[0m
    echo      [94mcd frontend ^&^& npm run dev[0m
    echo.
    echo   2. Open your browser:
    echo      [94mhttp://localhost:3000[0m
    echo.
    echo   3. Upload a PDF and start converting!
    echo.
) else (
    echo [91m================================================================[0m
    echo [91m  Setup Incomplete - Please fix the errors above               [0m
    echo [91m================================================================[0m
    echo.
    echo Common fixes:
    echo   * Install missing dependencies:
    echo     [94mcd backend ^&^& pip install -r requirements.txt[0m
    echo.
    echo   * Start your LLM provider:
    echo     [94mollama serve[0m  ^(for Ollama^)
    echo     [94mOr start LM Studio and enable the server[0m
    echo.
    echo   * Pull a model:
    echo     [94mollama pull llava[0m  ^(for vision support^)
    echo     [94mollama pull llama3[0m  ^(for text-only^)
    echo.
)

echo ================================================================
echo.
echo For more information:
echo   * Quick Start: [94mQUICKSTART.md[0m
echo   * Vision Guide: [94mVISION_GUIDE.md[0m
echo   * Examples: [94mEXAMPLES.md[0m
echo   * Full Docs: [94mREADME.md[0m
echo.

pause
