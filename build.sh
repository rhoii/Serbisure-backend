#!/bin/bash

# Install core packaging tools first (Force legacy support for Swagger)
echo "Upgrading pip and installing legacy-compatible tools..."
python3.12 -m pip install --upgrade pip "setuptools<70" wheel

# Install dependencies from requirements.txt
echo "Installing dependencies..."
python3.12 -m pip install -r requirements.txt

# Create static files directory
echo "Collecting static files..."
python3.12 manage.py collectstatic --no-input

# Run migrations
echo "Running database migrations..."
python3.12 manage.py migrate --no-input

# Seed data
echo "Seeding default services and users..."
python3.12 manage.py seed_services
python3.12 manage.py seed_users

echo "Build process completed!"
