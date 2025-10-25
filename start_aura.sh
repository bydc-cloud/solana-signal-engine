#!/bin/bash
#
# AURA Production Startup Script
# Cleanly starts server with proper configuration
#

cd "$(dirname "$0")"

echo "🛑 Stopping existing processes..."
pkill -9 -f "uvicorn aura_server" 2>/dev/null
pkill -9 -f "live_whale_tracker" 2>/dev/null
sleep 1

echo "🔍 Checking configuration..."
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    exit 1
fi

echo "🚀 Starting AURA server..."
python3 aura_server.py

# If python3 aura_server.py doesn't work, use uvicorn directly:
# python3 -m uvicorn aura_server:app --host 0.0.0.0 --port 8001 --reload
