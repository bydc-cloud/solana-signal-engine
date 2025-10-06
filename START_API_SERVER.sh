#!/bin/bash

# 🌐 HELIX API SERVER
# Control center API for Lovable dashboard
# ===========================================

echo "🌐 STARTING HELIX API SERVER"
echo "=========================================="

# Kill any existing instances
echo "🧹 Cleaning up existing API server..."
pkill -f "api_server.py" 2>/dev/null
sleep 2

# Change to correct directory
cd "/Users/johncox/Projects/helix/helix_production"

echo "🚀 Launching API server on http://localhost:8000..."
echo "📚 API documentation: http://localhost:8000/docs"
echo ""

# Run in background with logging
nohup python3 api_server.py > api_server.log 2>&1 &
API_PID=$!

echo "✅ API SERVER STARTED!"
echo "🔢 Process ID: $API_PID"
echo ""
echo "📊 Endpoints available:"
echo "   GET  /status        - Bot status and equity"
echo "   GET  /trades        - Recent trades"
echo "   GET  /alerts        - Recent alerts"
echo "   GET  /analytics/*   - Performance data"
echo "   GET  /config        - Current configuration"
echo "   POST /scanner/*     - Control scanner"
echo ""
echo "💡 To check logs: tail -f api_server.log"
echo "🛑 To stop: pkill -f api_server.py"
echo ""
echo "🎨 Ready for Lovable dashboard connection!"

# Save PID
echo $API_PID > api_server.pid
echo "📁 Process ID saved to api_server.pid"
