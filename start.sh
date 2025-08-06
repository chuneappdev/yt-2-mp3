#!/bin/bash

echo "Starting YouTube Downloader..."
echo "Python version: $(python --version)"
echo "Current directory: $(pwd)"
echo "Files in directory: $(ls -la)"

# Set default port if PORT is not set or is invalid
if [ -z "$PORT" ] || [ "$PORT" = "\$PORT" ]; then
    export PORT=5000
    echo "PORT not set or invalid, using default: $PORT"
else
    echo "Using PORT from environment: $PORT"
fi

# Create downloads directory
mkdir -p static/downloads
mkdir -p logs

# Test if the port is valid
if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
    echo "ERROR: PORT '$PORT' is not a valid number, using 5000"
    export PORT=5000
fi

echo "Starting app on port $PORT..."

# Start the application
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 300 --log-level info app:app
