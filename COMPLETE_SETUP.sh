#!/bin/bash
# Complete AURA Setup - One Command Deployment
# This script will guide you through the entire setup process

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║     AURA v0.3.0 - Complete Setup & Deployment             ║"
echo "║     MCP-First Autonomous Trading Intelligence              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Step 1: Prerequisites Check
echo -e "${BLUE}Step 1: Checking Prerequisites${NC}"
echo "----------------------------------------"

if ! command -v railway &> /dev/null; then
    echo -e "${YELLOW}⚠️  Railway CLI not installed${NC}"
    echo "Install with: npm install -g @railway/cli"
    echo "Then run this script again."
    exit 1
fi
echo -e "${GREEN}✓${NC} Railway CLI installed"

if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  Python 3 not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Python 3 installed"

echo ""

# Step 2: API Keys Collection
echo -e "${BLUE}Step 2: Collecting API Keys${NC}"
echo "----------------------------------------"
echo "You'll need the following API keys:"
echo "1. Helius (Solana RPC) - https://helix.xyz"
echo "2. Birdeye (DEX Data) - https://birdeye.so/developers"
echo "3. Firecrawl (Web Scraping) - https://firecrawl.dev"
echo "4. Telegram Bot Token - @BotFather on Telegram"
echo "5. Telegram Chat ID - Your user ID"
echo "6. CoinGecko (Optional) - https://www.coingecko.com/en/api"
echo ""

read -p "Do you have all API keys ready? (y/n): " HAS_KEYS

if [ "$HAS_KEYS" != "y" ]; then
    echo ""
    echo "Please obtain your API keys first, then run this script again."
    echo "See SETUP_GUIDE.md for detailed instructions."
    exit 0
fi

echo ""

# Step 3: Railway Project Link
echo -e "${BLUE}Step 3: Linking Railway Project${NC}"
echo "----------------------------------------"
echo "This will open an interactive prompt to select your project."
echo "Press Enter to continue..."
read

# Note: railway link requires interactive terminal
# User must run this manually

echo ""
echo -e "${YELLOW}⚠️  Run manually:${NC} railway link"
echo "Then continue to the next step."
echo ""
read -p "Have you linked the project? (y/n): " LINKED

if [ "$LINKED" != "y" ]; then
    echo "Please link your Railway project first:"
    echo "  railway link"
    echo "Then run this script again."
    exit 0
fi

echo ""

# Step 4: Set Environment Variables
echo -e "${BLUE}Step 4: Setting Environment Variables${NC}"
echo "----------------------------------------"

read -p "Helius API Key: " HELIUS_KEY
railway variables set HELIUS_API_KEY="$HELIUS_KEY"
echo -e "${GREEN}✓${NC} Helius API key set"

read -p "Birdeye API Key: " BIRDEYE_KEY
railway variables set BIRDEYE_API_KEY="$BIRDEYE_KEY"
echo -e "${GREEN}✓${NC} Birdeye API key set"

read -p "Firecrawl API Key: " FIRECRAWL_KEY
railway variables set FIRECRAWL_API_KEY="$FIRECRAWL_KEY"
echo -e "${GREEN}✓${NC} Firecrawl API key set"

read -p "Telegram Bot Token: " TELEGRAM_TOKEN
railway variables set TELEGRAM_BOT_TOKEN="$TELEGRAM_TOKEN"
echo -e "${GREEN}✓${NC} Telegram bot token set"

read -p "Telegram Chat ID: " TELEGRAM_CHAT
railway variables set TELEGRAM_CHAT_ID="$TELEGRAM_CHAT"
echo -e "${GREEN}✓${NC} Telegram chat ID set"

read -p "CoinGecko API Key (optional, press Enter to skip): " COINGECKO_KEY
if [ ! -z "$COINGECKO_KEY" ]; then
    railway variables set COINGECKO_API_KEY="$COINGECKO_KEY"
    echo -e "${GREEN}✓${NC} CoinGecko API key set"
fi

echo ""

# Step 5: Apply Database Migrations
echo -e "${BLUE}Step 5: Applying Database Migrations${NC}"
echo "----------------------------------------"
echo "Running migrations on Railway..."

railway run "python3 run_migrations.py"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Migrations applied successfully"
else
    echo -e "${YELLOW}⚠️  Migrations may have failed${NC}"
    echo "Check Railway logs: railway logs"
fi

echo ""

# Step 6: Restart Service
echo -e "${BLUE}Step 6: Restarting Service${NC}"
echo "----------------------------------------"
echo "Triggering Railway redeploy..."

railway redeploy

echo -e "${GREEN}✓${NC} Redeploy triggered"
echo ""
echo "Waiting 60 seconds for service to start..."
sleep 60

echo ""

# Step 7: Verification
echo -e "${BLUE}Step 7: Verifying Deployment${NC}"
echo "----------------------------------------"

BASE_URL="https://signal-railway-deployment-production.up.railway.app"

echo -n "Testing health endpoint... "
health_response=$(curl -s "$BASE_URL/health" || echo "failed")

if echo "$health_response" | grep -q "healthy"; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠️  (may still be starting)${NC}"
fi

echo -n "Testing watchlist API... "
watchlist_response=$(curl -s "$BASE_URL/api/watchlist" || echo "failed")

if echo "$watchlist_response" | grep -q "count"; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠️${NC}"
fi

echo ""

# Step 8: Next Steps
echo -e "${BLUE}Step 8: Final Steps${NC}"
echo "----------------------------------------"
echo "1. Test Telegram Bot:"
echo "   • Open Telegram"
echo "   • Search for your bot"
echo "   • Send: /start"
echo "   • Send: /help"
echo ""
echo "2. Monitor Logs:"
echo "   railway logs --follow"
echo ""
echo "3. View Dashboard:"
echo "   Run: cd dashboard && python3 -m http.server 8888"
echo "   Open: http://localhost:8888/app.html"
echo ""
echo "4. Full Verification:"
echo "   ./verify_deployment.sh"
echo ""

echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║               🎉 AURA Setup Complete! 🎉                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo "Deployment URL: $BASE_URL"
echo "Documentation: SETUP_GUIDE.md"
echo "Architecture: MCP_ARCHITECTURE_COMPLETE.md"
echo ""
echo "Support: https://github.com/bydc-cloud/solana-signal-engine"
echo ""
