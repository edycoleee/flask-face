#!/bin/bash

# Production mode - Clean output, no debug messages

# Suppress all warnings
export PYTHONWARNINGS=ignore
export ORT_LOGGING_LEVEL=3
export TF_CPP_MIN_LOG_LEVEL=3
export GLOG_minloglevel=3

# Activate venv
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run with Gunicorn (production server)
if command -v gunicorn &> /dev/null; then
    echo "Starting production server with Gunicorn..."
    gunicorn -w 2 -b 0.0.0.0:5001 --access-logfile - --error-logfile - 'run:app'
else
    echo "Gunicorn not found. Starting with Flask development server..."
    python run.py
fi
