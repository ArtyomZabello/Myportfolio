#!/bin/sh
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting Conduit API on port 8000..."
exec gunicorn -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 app.main:app
