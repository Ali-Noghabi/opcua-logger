#!/bin/bash

# Example script to run the OPC UA logger
# This script demonstrates how to use the logger

echo "Starting OPC UA Logger..."

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Virtual environment not found. Using system Python..."
fi

# Run the logger
python opcua_logger.py

echo "OPC UA Logger stopped."