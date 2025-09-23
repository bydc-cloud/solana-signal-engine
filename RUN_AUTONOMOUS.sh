#!/bin/bash

# 🎯 FULLY AUTONOMOUS MONEY PRINTER
# ===============================
# Runs in background - you can close terminal and it keeps working

echo "🎯 STARTING FULLY AUTONOMOUS MONEY PRINTER"
echo "=========================================="

# Kill any existing instances
echo "🧹 Cleaning up existing processes..."
pkill -f "REALITY_MOMENTUM_SCANNER.py" 2>/dev/null
sleep 2

# Change to correct directory
cd "/Users/johncox/Projects/helix/helix_production"

# Start in background with logging
echo "🚀 Launching autonomous scanner in background..."
echo "📝 Logs will be saved to: momentum_scanner.log"
echo "📱 Telegram signals will be sent continuously"
echo ""

# Run in background and detach from terminal
nohup python3 REALITY_MOMENTUM_SCANNER.py > autonomous_output.log 2>&1 &
SCANNER_PID=$!

echo "✅ AUTONOMOUS MONEY PRINTER STARTED!"
echo "🔢 Process ID: $SCANNER_PID"
echo ""
echo "📊 Status: FULLY AUTONOMOUS OPERATION"
echo "⚡ Scanning 100 tokens every 5 minutes"
echo "🎯 Sending 75+ strength signals to Telegram"
echo "📱 Jupiter swap links included"
echo ""
echo "💡 To check status: tail -f momentum_scanner.log"
echo "💡 To check output: tail -f autonomous_output.log"
echo "🛑 To stop: pkill -f REALITY_MOMENTUM_SCANNER.py"
echo ""
echo "🎉 YOU CAN NOW CLOSE THIS TERMINAL - SCANNER WILL KEEP RUNNING!"

# Save PID for easy management
echo $SCANNER_PID > scanner.pid
echo "📁 Process ID saved to scanner.pid"