#!/bin/bash

echo "Starting YouTube Downloader..."
echo "Python version: $(python --version)"
echo "Current directory: $(pwd)"
echo "Files in directory: $(ls -la)"
echo "PORT environment variable: $PORT"

# Create downloads directory
mkdir -p static/downloads

# Start the application
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 300 --log-level info app:app
