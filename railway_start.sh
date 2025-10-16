#!/bin/bash
# Railway startup script - clears Python cache before starting

echo "🧹 Cleaning Python cache..."
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

echo "🚀 Starting AURA server..."
exec uvicorn aura_server:app --host 0.0.0.0 --port ${PORT:-8000} --reload --reload-dir .
