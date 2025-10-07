#!/bin/bash
# AURA Startup Script for Railway
# Starts all services with proper error handling

set -e  # Exit on error

echo "🚀 Starting AURA v0.3.0..."

# Step 1: Initialize databases
echo "📊 Initializing databases..."
python3 init_db.py || echo "⚠️  init_db.py failed (might already exist)"
python3 init_aura_db.py || echo "⚠️  init_aura_db.py failed (might already exist)"

# Step 2: Apply migrations
echo "🔄 Applying database migrations..."
python3 run_migrations.py || echo "⚠️  Migrations failed (might already be applied)"

# Step 3: Start API server in background
echo "🌐 Starting API server on port ${PORT:-8000}..."
uvicorn aura_server:app --host 0.0.0.0 --port ${PORT:-8000} &
SERVER_PID=$!

# Give server 5 seconds to start
sleep 5

# Check if server is running
if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo "❌ API server failed to start"
    exit 1
fi

echo "✅ API server started (PID: $SERVER_PID)"

# Step 4: Start UNIFIED scanner in background (combines rule-based + intelligent)
echo "📡 Starting unified signal scanner..."
python3 unified_scanner.py &
SCANNER_PID=$!
echo "✅ Unified scanner started (PID: $SCANNER_PID)"

# Step 5: Start autonomous worker (optional)
echo "🤖 Starting autonomous worker..."
python3 aura_worker.py &
WORKER_PID=$!
echo "✅ Worker started (PID: $WORKER_PID)"

# Step 6: Start ingestion worker (optional)
echo "📈 Starting ingestion worker..."
python3 ingestion_worker.py &
INGESTION_PID=$!
echo "✅ Ingestion started (PID: $INGESTION_PID)"

echo ""
echo "🎉 AURA is fully operational!"
echo "   API Server: PID $SERVER_PID"
echo "   Scanner: PID $SCANNER_PID"
echo "   Worker: PID $WORKER_PID"
echo "   Ingestion: PID $INGESTION_PID"
echo ""

# Wait for API server (main process)
wait $SERVER_PID
