#!/bin/bash

# 🛑 STOP MONEY PRINTER
# ====================
# Clean shutdown of the autonomous scanner

echo "🛑 STOPPING REALITY MOMENTUM SCANNER"
echo "===================================="

# Kill the scanner process
echo "🔍 Finding scanner processes..."
PIDS=$(pgrep -f "REALITY_MOMENTUM_SCANNER.py")

if [ -z "$PIDS" ]; then
    echo "ℹ️  No scanner processes found running"
else
    echo "🛑 Stopping scanner processes: $PIDS"
    pkill -f "REALITY_MOMENTUM_SCANNER.py"
    sleep 2
    echo "✅ Scanner stopped"
fi

# Clean up any other related processes
echo "🧹 Cleaning up any other related processes..."
pkill -f "PRODUCTION_TELEGRAM_TRADER.py" 2>/dev/null
pkill -f "NUCLEAR_HELIX_SOCIAL_ENGINE.py" 2>/dev/null
pkill -f "FINAL_NUCLEAR_HELIX_ENGINE.py" 2>/dev/null

# Remove PID file if it exists
if [ -f "scanner.pid" ]; then
    rm scanner.pid
    echo "📁 Removed PID file"
fi

echo ""
echo "✅ MONEY PRINTER STOPPED"
echo "💡 To restart: ./RUN_AUTONOMOUS.sh"