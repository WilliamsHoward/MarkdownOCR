#!/bin/bash

# MarkDown OCR Setup Verification Script
# This script verifies that your system is properly configured for PDF to Markdown conversion

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║       MarkDown OCR v2.0 - Setup Verification              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Function to print success
print_success() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

# Function to print error
print_error() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

# Function to print info
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Checking Prerequisites"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    print_success "Python 3 installed: $PYTHON_VERSION"
else
    print_error "Python 3 not found"
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js installed: $NODE_VERSION"
else
    print_error "Node.js not found"
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    print_success "npm installed: $NPM_VERSION"
else
    print_error "npm not found"
fi

# Check Docker
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | awk '{print $3}' | sed 's/,//')
    print_success "Docker installed: $DOCKER_VERSION"
else
    print_warning "Docker not found (optional, but recommended)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. Checking LLM Provider"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check Ollama
if command -v ollama &> /dev/null; then
    print_success "Ollama CLI found"

    # Check if Ollama is running
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        print_success "Ollama server is running on port 11434"

        # List available models
        echo ""
        print_info "Available Ollama models:"
        ollama list 2>/dev/null | tail -n +2 | while read -r line; do
            MODEL_NAME=$(echo "$line" | awk '{print $1}')
            if [[ "$MODEL_NAME" == *"llava"* ]]; then
                echo "    ${GREEN}★${NC} $MODEL_NAME (Vision-capable)"
            else
                echo "    • $MODEL_NAME"
            fi
        done
        echo ""
    else
        print_warning "Ollama server is not running"
        print_info "Start it with: ollama serve"
    fi
else
    print_warning "Ollama not found"
    print_info "Install from: https://ollama.com/"
fi

# Check LM Studio
if curl -s http://localhost:1234/v1/models &> /dev/null; then
    print_success "LM Studio server detected on port 1234"
else
    print_warning "LM Studio server not detected on port 1234"
    print_info "If using LM Studio, make sure the server is started"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. Checking Project Structure"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check backend
if [ -d "backend" ]; then
    print_success "Backend directory found"

    # Check requirements.txt
    if [ -f "backend/requirements.txt" ]; then
        print_success "Backend requirements.txt exists"
    else
        print_error "Backend requirements.txt missing"
    fi

    # Check main.py
    if [ -f "backend/app/main.py" ]; then
        print_success "Backend main.py exists"
    else
        print_error "Backend main.py missing"
    fi
else
    print_error "Backend directory not found"
fi

# Check frontend
if [ -d "frontend" ]; then
    print_success "Frontend directory found"

    # Check package.json
    if [ -f "frontend/package.json" ]; then
        print_success "Frontend package.json exists"
    else
        print_error "Frontend package.json missing"
    fi
else
    print_error "Frontend directory not found"
fi

# Check docker-compose
if [ -f "docker-compose.yml" ]; then
    print_success "docker-compose.yml exists"
else
    print_warning "docker-compose.yml not found"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. Checking Python Dependencies"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -d "backend/venv" ] || [ -d "backend/.venv" ]; then
    print_success "Python virtual environment found"
else
    print_warning "No virtual environment detected"
    print_info "Create one with: cd backend && python3 -m venv venv"
fi

# Try to check if required packages are installed
if python3 -c "import fastapi" 2>/dev/null; then
    print_success "FastAPI installed"
else
    print_warning "FastAPI not installed"
    print_info "Install with: pip install -r backend/requirements.txt"
fi

if python3 -c "import fitz" 2>/dev/null; then
    print_success "PyMuPDF installed"
else
    print_warning "PyMuPDF not installed"
fi

if python3 -c "import PIL" 2>/dev/null; then
    print_success "Pillow (PIL) installed - Vision support ready"
else
    print_warning "Pillow not installed - Required for vision model support"
    print_info "Install with: pip install Pillow"
fi

if python3 -c "import langchain_openai" 2>/dev/null; then
    print_success "LangChain OpenAI installed"
else
    print_warning "LangChain OpenAI not installed"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5. Checking Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "backend/.env" ]; then
    print_success "Environment file (.env) found"

    # Read and display key settings
    echo ""
    print_info "Current configuration:"

    if grep -q "USE_VISION_MODEL" backend/.env; then
        VISION_ENABLED=$(grep "USE_VISION_MODEL" backend/.env | cut -d'=' -f2)
        if [[ "$VISION_ENABLED" == *"true"* ]]; then
            echo "    ${GREEN}★${NC} Vision Model: ENABLED"
        else
            echo "    • Vision Model: DISABLED (text-only mode)"
        fi
    fi

    if grep -q "VISION_MODEL" backend/.env; then
        VISION_MODEL=$(grep "VISION_MODEL" backend/.env | cut -d'=' -f2)
        echo "    • Vision Model: $VISION_MODEL"
    fi

    if grep -q "LLM_MODEL" backend/.env; then
        LLM_MODEL=$(grep "LLM_MODEL" backend/.env | cut -d'=' -f2)
        echo "    • Text Model: $LLM_MODEL"
    fi

    if grep -q "PDF_DPI" backend/.env; then
        PDF_DPI=$(grep "PDF_DPI" backend/.env | cut -d'=' -f2)
        echo "    • PDF DPI: $PDF_DPI"
    fi

    echo ""
else
    print_warning "No .env file found (using defaults)"
    print_info "Copy env.template to .env to customize settings"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6. Testing LLM Connection"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "backend/test_llm_connection.py" ]; then
    print_info "Running LLM connection test..."
    echo ""

    cd backend
    if python3 test_llm_connection.py; then
        cd ..
        print_success "LLM connection test passed!"
    else
        cd ..
        print_error "LLM connection test failed"
        print_info "Check the output above for troubleshooting steps"
    fi
else
    print_warning "LLM test script not found"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}✓ Passed:${NC} $PASSED"
echo -e "${YELLOW}⚠ Warnings:${NC} $WARNINGS"
echo -e "${RED}✗ Failed:${NC} $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  🎉 Setup Complete! You're ready to start converting!     ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Start the application:"
    echo "     ${BLUE}docker-compose up --build${NC}"
    echo "     OR"
    echo "     ${BLUE}cd backend && uvicorn app.main:app --reload${NC}"
    echo "     ${BLUE}cd frontend && npm run dev${NC}"
    echo ""
    echo "  2. Open your browser:"
    echo "     ${BLUE}http://localhost:3000${NC}"
    echo ""
    echo "  3. Upload a PDF and start converting!"
    echo ""
else
    echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ⚠️  Setup Incomplete - Please fix the errors above       ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Common fixes:"
    echo "  • Install missing dependencies:"
    echo "    ${BLUE}cd backend && pip install -r requirements.txt${NC}"
    echo ""
    echo "  • Start your LLM provider:"
    echo "    ${BLUE}ollama serve${NC}  (for Ollama)"
    echo "    ${BLUE}# Or start LM Studio and enable the server${NC}"
    echo ""
    echo "  • Pull a model:"
    echo "    ${BLUE}ollama pull llava${NC}  (for vision support)"
    echo "    ${BLUE}ollama pull llama3${NC}  (for text-only)"
    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "For more information:"
echo "  • Quick Start: ${BLUE}QUICKSTART.md${NC}"
echo "  • Vision Guide: ${BLUE}VISION_GUIDE.md${NC}"
echo "  • Examples: ${BLUE}EXAMPLES.md${NC}"
echo "  • Full Docs: ${BLUE}README.md${NC}"
echo ""
