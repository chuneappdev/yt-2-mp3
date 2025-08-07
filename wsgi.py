"""
WSGI entry point for Railway deployment
"""
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set production environment for Railway
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_DEBUG', 'False')

from app import app

# Railway will handle the port automatically when using WSGI
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting app on Railway port: {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
