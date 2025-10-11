#!/bin/bash
# Set Railway environment variables using Railway CLI

echo "🔧 Setting Railway Environment Variables"
echo "========================================="
echo ""

# Load .env
if [ -f ".env" ]; then
    source .env
fi

# Railway project/service IDs
PROJECT_ID="900cdde4-c62a-4659-a110-fd6151773887"
SERVICE_ID="0785d30d-a931-47ec-9172-1a01b7adbea8"

echo "Setting variables for AURA deployment..."
echo ""

# Set Telegram token
if [ ! -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "✅ TELEGRAM_BOT_TOKEN"
    railway variables set TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN" 2>/dev/null || echo "  (manual set required)"
fi

if [ ! -z "$TELEGRAM_CHAT_ID" ]; then
    echo "✅ TELEGRAM_CHAT_ID"
    railway variables set TELEGRAM_CHAT_ID="$TELEGRAM_CHAT_ID" 2>/dev/null || echo "  (manual set required)"
fi

# Set API keys
if [ ! -z "$BIRDEYE_API_KEY" ]; then
    echo "✅ BIRDEYE_API_KEY"
    railway variables set BIRDEYE_API_KEY="$BIRDEYE_API_KEY" 2>/dev/null || echo "  (manual set required)"
fi

if [ ! -z "$HELIUS_API_KEY" ]; then
    echo "✅ HELIUS_API_KEY"
    railway variables set HELIUS_API_KEY="$HELIUS_API_KEY" 2>/dev/null || echo "  (manual set required)"
fi

if [ ! -z "$NASEN_API_KEY" ]; then
    echo "✅ NASEN_API_KEY"
    railway variables set NASEN_API_KEY="$NASEN_API_KEY" 2>/dev/null || echo "  (manual set required)"
fi

# Set GRAD config
echo "✅ Setting GRAD trading config..."
railway variables set GRAD_ENABLED="$GRAD_ENABLED" 2>/dev/null || true
railway variables set GRAD_MODE="$GRAD_MODE" 2>/dev/null || true
railway variables set GRAD_PAPER_START_USD="$GRAD_PAPER_START_USD" 2>/dev/null || true
railway variables set GRAD_MIN_SCORE="$GRAD_MIN_SCORE" 2>/dev/null || true

echo ""
echo "⚠️  IMPORTANT: AI Keys for Telegram bot"
echo ""
echo "You need to add ONE of these manually in Railway dashboard:"
echo "  Option 1 (preferred): ANTHROPIC_API_KEY=<your-claude-key>"
echo "  Option 2 (fallback):  OPENAI_API_KEY=<your-openai-key>"
echo ""
echo "Go to: https://railway.app/project/$PROJECT_ID/service/$SERVICE_ID"
echo "Click 'Variables' tab and add the key"
echo ""
echo "========================================="
echo "✅ Core variables set!"
echo ""
