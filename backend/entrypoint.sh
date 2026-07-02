#!/bin/sh
set -e

echo "Waiting for database..."

# Apply database migrations
flask --app app db upgrade

echo "Starting Gunicorn..."

exec gunicorn app:app \
    --bind 0.0.0.0:5000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
