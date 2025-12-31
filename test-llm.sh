#!/bin/bash

# MarkDown OCR - LLM Connection Test Wrapper
# This script provides a convenient way to test your LLM connection

set -e

echo "=========================================="
echo "MarkDown OCR - LLM Connection Test"
echo "=========================================="
echo ""

# Change to backend directory
cd "$(dirname "$0")/backend"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
if [ ! -f "venv/.installed" ]; then
    echo "📦 Installing dependencies..."
    pip install -q -r requirements.txt
    touch venv/.installed
    echo "✅ Dependencies installed"
    echo ""
fi

# Run the test script
echo "🧪 Running LLM connection test..."
echo ""
python test_llm_connection.py

# Deactivate virtual environment
deactivate

echo ""
echo "Test complete!"
