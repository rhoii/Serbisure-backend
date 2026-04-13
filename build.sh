#!/bin/bash

# Install dependencies
echo "Installing dependencies..."
python3.12 -m pip install -r requirements.txt

# Create static files directory
echo "Collecting static files..."
python3.12 manage.py collectstatic --no-input

# Run migrations
echo "Running database migrations..."
python3.12 manage.py migrate --no-input

echo "Build process completed!"
