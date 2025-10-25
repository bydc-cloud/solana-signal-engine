#!/bin/bash
# Start AURA server with environment variables loaded

cd /Users/johncox/Projects/helix/helix_production

# Load environment variables
export $(cat .env | xargs)

# Kill any existing server
pkill -f "uvicorn aura_server" 2>/dev/null

# Wait for clean shutdown
sleep 2

# Start server
PORT=8001 python3 -m uvicorn aura_server:app --host 0.0.0.0 --port 8001 --reload
