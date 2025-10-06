#!/bin/bash
# Railway Environment Variables Setup Script
# Usage: ./setup_railway_vars.sh

set -e

echo "🔧 AURA Railway Environment Setup"
echo "=================================="
echo ""

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Install with:"
    echo "   npm install -g @railway/cli"
    exit 1
fi

echo "📝 Please provide your API keys:"
echo ""

# Helius
read -p "Helius API Key (https://helius.xyz): " HELIUS_KEY
if [ ! -z "$HELIUS_KEY" ]; then
    railway variables set HELIUS_API_KEY="$HELIUS_KEY"
    echo "✅ Helius API key set"
fi

# Birdeye
read -p "Birdeye API Key (https://birdeye.so/developers): " BIRDEYE_KEY
if [ ! -z "$BIRDEYE_KEY" ]; then
    railway variables set BIRDEYE_API_KEY="$BIRDEYE_KEY"
    echo "✅ Birdeye API key set"
fi

# Firecrawl
read -p "Firecrawl API Key (https://firecrawl.dev): " FIRECRAWL_KEY
if [ ! -z "$FIRECRAWL_KEY" ]; then
    railway variables set FIRECRAWL_API_KEY="$FIRECRAWL_KEY"
    echo "✅ Firecrawl API key set"
fi

# Telegram Bot Token
read -p "Telegram Bot Token (from @BotFather): " TELEGRAM_TOKEN
if [ ! -z "$TELEGRAM_TOKEN" ]; then
    railway variables set TELEGRAM_BOT_TOKEN="$TELEGRAM_TOKEN"
    echo "✅ Telegram bot token set"
fi

# Telegram Chat ID
read -p "Telegram Chat ID (your user ID): " TELEGRAM_CHAT
if [ ! -z "$TELEGRAM_CHAT" ]; then
    railway variables set TELEGRAM_CHAT_ID="$TELEGRAM_CHAT"
    echo "✅ Telegram chat ID set"
fi

# CoinGecko (optional)
read -p "CoinGecko API Key (optional, press Enter to skip): " COINGECKO_KEY
if [ ! -z "$COINGECKO_KEY" ]; then
    railway variables set COINGECKO_API_KEY="$COINGECKO_KEY"
    echo "✅ CoinGecko API key set"
fi

echo ""
echo "🎉 Environment variables configured!"
echo ""
echo "Next steps:"
echo "1. Run migrations: railway run 'python3 run_migrations.py'"
echo "2. Restart service: railway redeploy"
echo "3. Check health: curl https://signal-railway-deployment-production.up.railway.app/health"
echo "4. Test Telegram: Send /start to your bot"
echo ""
