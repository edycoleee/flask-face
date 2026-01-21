#!/bin/bash

# Script untuk run Flask server di Raspberry Pi 5 tanpa warning

echo "=================================================="
echo "Starting Flask Face Recognition Server"
echo "=================================================="
echo "Raspberry Pi 5 - CPU Mode (No GPU)"
echo ""

# Set environment variables untuk suppress warnings
export ORT_LOGGING_LEVEL=3
export TF_CPP_MIN_LOG_LEVEL=3
export GLOG_minloglevel=3
export PYTHONWARNINGS=ignore

# Activate virtual environment
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run Flask server
echo "Starting server on http://0.0.0.0:5001"
echo "Press CTRL+C to stop"
echo ""

python run.py
