#!/bin/bash

# Crypto Price Alert Assistant - Startup Script
echo "🚀 CRYPTO PRICE ALERT ASSISTANT"
echo "=================================="
echo "Starting AI-Powered Crypto Monitoring System..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Start the application
echo "🚀 Starting application..."
python run_app.py
