#!/bin/bash

# Startup script for Honeypot System

echo "========================================"
echo "  Agentic Honey-Pot System Startup"
echo "========================================"

# Check if Ollama is running
echo ""
echo "Checking Ollama..."
if ! curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
    echo "❌ Ollama is not running!"
    echo "Please start Ollama first: ollama serve"
    exit 1
fi
echo "✓ Ollama is running"

# Check if model is available
echo ""
echo "Checking model..."
if ! ollama list | grep -q "llama3.2:3b"; then
    echo "❌ Model llama3.2:3b not found!"
    echo "Pulling model... (this may take a few minutes)"
    ollama pull llama3.2:3b
fi
echo "✓ Model is available"

# Check Python dependencies
echo ""
echo "Checking dependencies..."
if ! python -c "import fastapi" 2>/dev/null; then
    echo "❌ Dependencies not installed!"
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi
echo "✓ Dependencies installed"

# Check config
echo ""
echo "Checking configuration..."
if grep -q "your-secure-api-key-change-this" config.py; then
    echo "⚠️  WARNING: Default API key detected!"
    echo "Please change API_KEY in config.py for security"
    echo ""
fi

# Start server
echo ""
echo "========================================"
echo "Starting server..."
echo "========================================"
echo ""
echo "API will be available at: http://localhost:8000"
echo "API Key: Check config.py"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python main.py
