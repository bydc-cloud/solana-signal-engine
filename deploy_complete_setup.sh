#!/bin/bash
# Complete Railway deployment setup script

set -e

echo "🚀 AURA v0.3.0 - Complete Railway Setup"
echo "========================================"
echo ""

# 1. Set environment variables on Railway
echo "📝 Step 1: Setting Railway environment variables..."
echo ""

# Check if we have the API keys locally
if [ -f ".env" ]; then
    echo "Found .env file, reading keys..."
    source .env
else
    echo "No .env file found, will use manual input"
fi

# Set ANTHROPIC_API_KEY
if [ ! -z "$ANTHROPIC_API_KEY" ]; then
    echo "Setting ANTHROPIC_API_KEY..."
    railway variables --set ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" 2>/dev/null || echo "  ⚠️  Railway CLI not linked, skipping..."
else
    echo "⚠️  ANTHROPIC_API_KEY not found in .env"
fi

# Set OPENAI_API_KEY
if [ ! -z "$OPENAI_API_KEY" ]; then
    echo "Setting OPENAI_API_KEY..."
    railway variables --set OPENAI_API_KEY="$OPENAI_API_KEY" 2>/dev/null || echo "  ⚠️  Railway CLI not linked, skipping..."
else
    echo "⚠️  OPENAI_API_KEY not found in .env"
fi

# Set TELEGRAM_BOT_TOKEN
if [ ! -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "Setting TELEGRAM_BOT_TOKEN..."
    railway variables --set TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN" 2>/dev/null || echo "  ⚠️  Railway CLI not linked, skipping..."
fi

echo ""
echo "✅ Step 1 complete"
echo ""

# 2. Upload database to Railway
echo "📦 Step 2: Preparing database for Railway..."
echo ""

if [ -f "aura.db" ]; then
    echo "Found aura.db locally"

    # Check if database has whale wallets
    WALLET_COUNT=$(sqlite3 aura.db "SELECT COUNT(*) FROM tracked_wallets WHERE is_active = 1" 2>/dev/null || echo "0")
    echo "  Whale wallets: $WALLET_COUNT"

    if [ "$WALLET_COUNT" -gt "0" ]; then
        echo "  Creating database dump..."
        sqlite3 aura.db ".dump tracked_wallets" > whale_wallets.sql

        echo "  Dump created: whale_wallets.sql"
        echo "  ℹ️  You'll need to import this on Railway manually via SSH or database manager"
    else
        echo "  ⚠️  No whale wallets in database"
    fi
else
    echo "⚠️  aura.db not found"
fi

echo ""
echo "✅ Step 2 complete"
echo ""

# 3. Create scanner startup script for Railway
echo "🔧 Step 3: Creating scanner startup script..."
echo ""

cat > start_scanner_railway.sh << 'EOF'
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
EOF

chmod +x start_scanner_railway.sh

echo "  Created: start_scanner_railway.sh"
echo ""
echo "✅ Step 3 complete"
echo ""

# 4. Create Railway deployment test script
echo "🧪 Step 4: Creating deployment test script..."
echo ""

cat > test_railway_deployment.sh << 'EOF'
#!/bin/bash
# Test Railway deployment

BASE_URL="https://signal-railway-deployment-production.up.railway.app"

echo "Testing AURA deployment at: $BASE_URL"
echo ""

echo "1. Status endpoint:"
curl -s "$BASE_URL/status" | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"   Scanner: {d['scanner_status']}, DB: {d['database_initialized']}\")"
echo ""

echo "2. Signals endpoint:"
curl -s "$BASE_URL/api/aura/scanner/signals" | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"   Signals: {d.get('count', 0)}\")"
echo ""

echo "3. Wallets endpoint:"
curl -s "$BASE_URL/api/aura/wallets" | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"   Wallets: {d.get('count', 0)}\")"
echo ""

echo "4. Portfolio endpoint:"
curl -s "$BASE_URL/api/aura/portfolio" | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"   Positions: {len(d.get('open_positions', []))}\")"
echo ""

echo "5. Logs endpoint:"
curl -s "$BASE_URL/api/aura/logs" | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"   Log entries: {d.get('count', 0)}\")"
echo ""

echo "6. Social endpoint:"
curl -s "$BASE_URL/api/aura/social/momentum" | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"   Trends: {d.get('count', 0)}\")"
echo ""

echo "7. Dashboard:"
STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/dashboard")
echo "   HTTP $STATUS_CODE"
echo ""

echo "✅ Test complete"
EOF

chmod +x test_railway_deployment.sh

echo "  Created: test_railway_deployment.sh"
echo ""
echo "✅ Step 4 complete"
echo ""

# 5. Commit and deploy
echo "🚀 Step 5: Deploying to Railway..."
echo ""

git add -A
git commit -m "deploy: Add Railway setup and scanner startup scripts

- Add complete setup script for Railway environment
- Add scanner startup script for background execution
- Add deployment test script
- Export whale wallet data for Railway import

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>" 2>/dev/null || echo "Nothing to commit"

echo "Deploying to Railway..."
railway up --detach 2>/dev/null || echo "⚠️  Railway CLI not linked, manual deployment needed"

echo ""
echo "✅ Step 5 complete"
echo ""

echo "========================================"
echo "✅ Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Go to Railway dashboard: https://railway.app/project/900cdde4-c62a-4659-a110-fd6151773887"
echo "2. Add environment variables manually if CLI failed:"
echo "   - ANTHROPIC_API_KEY"
echo "   - OPENAI_API_KEY"
echo "   - TELEGRAM_BOT_TOKEN"
echo "3. Wait 2 minutes for deployment"
echo "4. Run: ./test_railway_deployment.sh"
echo ""
echo "To start scanner on Railway, use Railway shell:"
echo "  railway shell"
echo "  ./start_scanner_railway.sh"
echo ""
