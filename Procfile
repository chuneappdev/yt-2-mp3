# Production deployment with Gunicorn
web: gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 4 --timeout 300 app:app
