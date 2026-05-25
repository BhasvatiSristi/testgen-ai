#!/usr/bin/env bash
set -e
# Use Replit/hosting provided PORT if set, otherwise default to 8000
PORT=${PORT:-8000}
echo "Starting backend on port $PORT"
uvicorn backend.api:app --host 0.0.0.0 --port "$PORT"
