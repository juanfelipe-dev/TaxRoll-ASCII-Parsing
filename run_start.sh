#!/bin/bash

# Tax Roll ASCII Parsing - Render.com Start Script
# This script installs dependencies and starts the Flask application

# Install Python dependencies
pip install -r requirements.txt

# Run the Flask app
# Render.com provides the PORT environment variable
python app.py
