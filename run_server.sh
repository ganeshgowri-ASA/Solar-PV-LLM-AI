#!/bin/bash

# Run Solar PV LLM AI Vector Store API Server

echo "Starting Solar PV LLM AI Vector Store API..."
echo "============================================"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file from .env.example and configure your API keys"
    echo ""
    echo "  cp .env.example .env"
    echo "  # Edit .env with your PINECONE_API_KEY and OPENAI_API_KEY"
    echo ""
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "No virtual environment found. Creating one..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing/updating dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "✓ Setup complete!"
echo ""
echo "Starting API server..."
echo "API will be available at: http://localhost:8000"
echo "Swagger docs at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the server
python -m src.main
