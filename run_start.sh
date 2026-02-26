#!/bin/bash

# Tax Roll ASCII Parsing - Render.com Start Script
# This script installs dependencies and starts the Flask application

# Install Python dependencies
pip install -r requirements.txt

# Run the Flask app
# Prefer gunicorn for production; fall back to built-in server
if command -v gunicorn >/dev/null 2>&1; then
    echo "Starting with gunicorn"
    gunicorn app:app --bind 0.0.0.0:${PORT:-5000}
else
    echo "Gunicorn not found, running via python"
    python app.py
fi
