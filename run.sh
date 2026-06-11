#!/bin/bash
echo "Checking Student Result Management System setup..."
python3 check_setup.py
if [ $? -ne 0 ]; then
    echo ""
    echo "Setup check failed. Please install dependencies manually:"
    echo "pip install -r requirements.txt"
    exit 1
fi
echo ""
echo "Starting application..."
python3 main.py
