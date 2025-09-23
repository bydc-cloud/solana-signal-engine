#!/bin/bash

# 🚀 AUTONOMOUS MONEY PRINTER STARTUP SCRIPT
# =========================================
# This script ensures clean startup and autonomous operation

echo "🚀 STARTING REALITY MOMENTUM SCANNER - AUTONOMOUS MONEY PRINTER"
echo "=============================================================="

# Kill any existing instances to prevent conflicts
echo "🧹 Cleaning up any existing processes..."
pkill -f "REALITY_MOMENTUM_SCANNER.py" 2>/dev/null
pkill -f "PRODUCTION_TELEGRAM_TRADER.py" 2>/dev/null
pkill -f "NUCLEAR_HELIX_SOCIAL_ENGINE.py" 2>/dev/null
pkill -f "FINAL_NUCLEAR_HELIX_ENGINE.py" 2>/dev/null

sleep 2

# Change to the correct directory
cd "/Users/johncox/Projects/helix/helix_production"

echo "✅ Environment cleaned"
echo "📂 Working directory: $(pwd)"
echo ""

# Check environment file exists
if [ ! -f ".env" ]; then
    echo "❌ ERROR: .env file not found!"
    echo "   Make sure your API keys are in the .env file"
    exit 1
fi

echo "✅ Environment file found"

# Check Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: python3 not found!"
    exit 1
fi

echo "✅ Python3 available"

# Start the Reality Momentum Scanner
echo ""
echo "🚀 LAUNCHING AUTONOMOUS MONEY PRINTER..."
echo "⚡ Reality Momentum Scanner starting..."
echo "📱 Signals will be sent to your Telegram"
echo "🔗 Jupiter swap links included for immediate trading"
echo ""
echo "📊 System will:"
echo "   • Scan 100 tokens every 5 minutes"
echo "   • Send only 75+ signal strength opportunities"
echo "   • Include risk assessment and volume validation"
echo "   • Prevent spam with anti-duplicate protection"
echo ""
echo "💡 To stop: Press Ctrl+C or run 'pkill -f REALITY_MOMENTUM_SCANNER.py'"
echo ""

# Start the scanner with proper error handling
python3 REALITY_MOMENTUM_SCANNER.py