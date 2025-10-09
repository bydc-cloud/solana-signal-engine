#!/bin/bash
# Start scanner on Railway in background

echo "Starting AURA scanner on Railway..."

# Check if scanner is already running
if pgrep -f "REALITY_MOMENTUM_SCANNER.py" > /dev/null; then
    echo "Scanner already running"
    exit 0
fi

# Start scanner in background
nohup python3 REALITY_MOMENTUM_SCANNER.py > scanner.log 2>&1 &
SCANNER_PID=$!

echo "Scanner started with PID: $SCANNER_PID"
echo $SCANNER_PID > scanner.pid

# Wait a bit and check if it's running
sleep 5

if ps -p $SCANNER_PID > /dev/null; then
    echo "✅ Scanner is running"
    tail -20 scanner.log
else
    echo "❌ Scanner failed to start"
    tail -50 scanner.log
    exit 1
fi
