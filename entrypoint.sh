#!/bin/bash
set -e

echo "Running database migrations..."
/app/.venv/bin/alembic upgrade head

echo "Starting bot..."
/app/.venv/bin/python -m src.main

