#!/bin/bash
# Quick start script for local development

echo "🚀 Starting Immich → Google Photos Sync (Development Mode)"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env and add your credentials"
    echo ""
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Create data directory
mkdir -p data/logs

# Export environment variables
export DATABASE_PATH="./data/app.db"
export LOG_PATH="./data/logs"

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Starting server at http://localhost:8080"
echo "Press Ctrl+C to stop"
echo ""

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
