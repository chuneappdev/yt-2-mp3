#!/bin/bash

# YouTube Downloader - Run Script
# This script will start the YouTube downloader on the first available port

echo "🎵 Starting YouTube Downloader..."

# Check if virtual environment exists
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    source .venv/bin/activate
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file from template..."
    cp .env.example .env
fi

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 1  # Port is in use
    else
        return 0  # Port is available
    fi
}

# Try different ports
PORTS=(5000 8080 3000 8000 8888 9000)
AVAILABLE_PORT=""

for port in "${PORTS[@]}"; do
    if check_port $port; then
        AVAILABLE_PORT=$port
        break
    fi
done

if [ -z "$AVAILABLE_PORT" ]; then
    echo "❌ No available ports found. Please free up one of these ports: ${PORTS[*]}"
    exit 1
fi

echo "🚀 Starting server on port $AVAILABLE_PORT..."
echo "🌐 Open http://localhost:$AVAILABLE_PORT in your browser"
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

# Set the port and start the application
PORT=$AVAILABLE_PORT python app.py
