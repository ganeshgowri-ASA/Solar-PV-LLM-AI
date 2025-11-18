#!/bin/bash

# ============================================
# Solar PV LLM AI - Setup Script
# ============================================
# This script sets up the development environment

set -e  # Exit on error

echo "=========================================="
echo "Solar PV LLM AI - Environment Setup"
echo "=========================================="
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "📝 Copying .env.example to .env..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your API keys before continuing!"
    echo ""
    read -p "Have you configured your API keys in .env? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Please configure .env file and run this script again"
        exit 1
    fi
else
    echo "✅ .env file found"
fi

echo ""
echo "=========================================="
echo "Checking prerequisites..."
echo "=========================================="

# Check Docker
if command -v docker &> /dev/null; then
    echo "✅ Docker is installed: $(docker --version)"
else
    echo "❌ Docker is not installed"
    echo "   Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose is installed: $(docker-compose --version)"
else
    echo "❌ Docker Compose is not installed"
    echo "   Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo ""
echo "=========================================="
echo "Building Docker containers..."
echo "=========================================="

docker-compose build

echo ""
echo "=========================================="
echo "Starting services..."
echo "=========================================="

docker-compose up -d postgres redis

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

echo ""
echo "=========================================="
echo "Checking service health..."
echo "=========================================="

docker-compose ps

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Start all services: docker-compose up -d"
echo "  2. View logs: docker-compose logs -f"
echo "  3. Access frontend: http://localhost:3000"
echo "  4. Access backend: http://localhost:8000"
echo "  5. Access API docs: http://localhost:8000/docs"
echo ""
echo "To stop services: docker-compose down"
echo ""
