#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "Creating venv..."
python3 -m venv venv

echo "Activating venv..."
source venv/bin/activate

echo "Upgrading pip..."
python -m pip install --upgrade pip

echo "Installing dependencies..."
python -m pip install torch ultralytics boto3 opencv-python numpy

echo "Setup complete!"
echo "To use: source venv/bin/activate"