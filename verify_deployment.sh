#!/bin/bash
# AURA Deployment Verification Script
# Checks all components and reports status

set -e

BASE_URL="https://signal-railway-deployment-production.up.railway.app"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 AURA v0.3.0 Deployment Verification"
echo "======================================"
echo ""

# Function to check endpoint
check_endpoint() {
    local name=$1
    local endpoint=$2
    local expected=$3

    echo -n "Testing $name... "

    response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint" || echo "000")
    status_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | sed '$ d')

    if [ "$status_code" = "200" ]; then
        if [ ! -z "$expected" ]; then
            if echo "$body" | grep -q "$expected"; then
                echo -e "${GREEN}✓${NC}"
                return 0
            else
                echo -e "${YELLOW}⚠ (unexpected response)${NC}"
                return 1
            fi
        else
            echo -e "${GREEN}✓${NC}"
            return 0
        fi
    else
        echo -e "${RED}✗ (HTTP $status_code)${NC}"
        return 1
    fi
}

# Test 1: System Health
echo "1️⃣  System Health Check"
check_endpoint "Health endpoint" "/health" "status"
check_endpoint "Status endpoint" "/status" "scanner"
echo ""

# Test 2: Dashboard API
echo "2️⃣  Dashboard API Endpoints"
check_endpoint "Watchlist API" "/api/watchlist" "count"
check_endpoint "Alerts API" "/api/alerts" ""
check_endpoint "Portfolio API" "/api/portfolio" ""
check_endpoint "Strategies API" "/api/strategies" ""
echo ""

# Test 3: Database Migrations
echo "3️⃣  Database Tables"
response=$(curl -s "$BASE_URL/api/alerts")
if echo "$response" | grep -q "no such table"; then
    echo -e "${RED}✗ Migrations not applied${NC}"
    echo "   Run: railway run 'python3 run_migrations.py'"
else
    echo -e "${GREEN}✓ Database migrations applied${NC}"
fi
echo ""

# Test 4: Workers
echo "4️⃣  Background Workers"
echo "   Check Railway logs for:"
echo "   • AURA Autonomous Worker starting"
echo "   • AURA Ingestion Worker starting"
echo "   • Signal generation logs"
echo ""

# Test 5: Environment Variables
echo "5️⃣  Environment Variables (check Railway dashboard)"
echo "   Required:"
echo "   • HELIUS_API_KEY"
echo "   • BIRDEYE_API_KEY"
echo "   • FIRECRAWL_API_KEY"
echo "   • TELEGRAM_BOT_TOKEN"
echo "   • TELEGRAM_CHAT_ID"
echo "   Optional:"
echo "   • COINGECKO_API_KEY"
echo ""

# Test 6: MCP Health
echo "6️⃣  MCP Toolkit Status"
if [ -f "mcp_health_check.py" ]; then
    echo "   Run locally: python3 mcp_health_check.py"
else
    echo "   mcp_health_check.py not found"
fi
echo ""

# Summary
echo "======================================"
echo "📊 Summary"
echo "======================================"
echo ""
echo "Deployment URL: $BASE_URL"
echo ""
echo "Next steps:"
echo "1. If migrations failed, run: railway run 'python3 run_migrations.py'"
echo "2. Set API keys: ./setup_railway_vars.sh"
echo "3. Test Telegram: Send /start to your bot"
echo "4. Check logs: railway logs --follow"
echo ""
echo "Documentation: See SETUP_GUIDE.md"
echo ""
