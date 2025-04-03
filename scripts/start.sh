#!/bin/bash
set -e

# Run migrations
alembic upgrade head

# Start the application server
if [ "$ENVIRONMENT" = "production" ]; then
    echo "Starting in production mode"
    exec gunicorn app.main:app \
        --workers 4 \
        --worker-class uvicorn.workers.UvicornWorker \
        --bind 0.0.0.0:8000
else
    echo "Starting in development mode"
    exec uvicorn app.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --reload
fi
