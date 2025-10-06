#!/bin/bash
# Complete deployment and verification script
# Run this once Railway CLI is set up

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║     AURA v0.3.0 - Complete Deployment & Verification         ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

BASE_URL="https://signal-railway-deployment-production.up.railway.app"

# Step 1: Check if Railway CLI is available
echo -e "${BLUE}Step 1: Checking Railway CLI${NC}"
echo "─────────────────────────────────────────"

if ! command -v railway &> /dev/null; then
    echo -e "${RED}✗ Railway CLI not found${NC}"
    echo ""
    echo "Install with: npm install -g @railway/cli"
    echo "Then run this script again."
    exit 1
fi

echo -e "${GREEN}✓ Railway CLI installed${NC}"
echo ""

# Step 2: Check Railway service health
echo -e "${BLUE}Step 2: Checking Railway Service Health${NC}"
echo "─────────────────────────────────────────"

echo -n "Testing $BASE_URL/health... "

health_response=$(curl -s -w "\n%{http_code}" "$BASE_URL/health" 2>/dev/null || echo "failed\n000")
status_code=$(echo "$health_response" | tail -n 1)
body=$(echo "$health_response" | sed '$ d')

if [ "$status_code" = "200" ]; then
    echo -e "${GREEN}✓ Service is healthy${NC}"
    SERVICE_HEALTHY=true
elif [ "$status_code" = "502" ]; then
    echo -e "${YELLOW}⚠ Service is down (502)${NC}"
    echo ""
    echo "The service may still be building or has crashed."
    echo "Checking Railway logs..."
    echo ""

    # Try to get logs
    railway logs 2>&1 | tail -50 || echo "Could not fetch logs (try: railway logs)"

    echo ""
    echo -e "${YELLOW}Action Required:${NC}"
    echo "1. Check Railway dashboard: https://railway.app/dashboard"
    echo "2. Look for build errors or startup crashes"
    echo "3. Common issues:"
    echo "   - Missing dependencies in requirements.txt"
    echo "   - Database path errors"
    echo "   - Port binding issues"
    echo ""
    read -p "Press Enter once service is healthy, or Ctrl+C to exit..."

    # Recheck
    health_response=$(curl -s -w "\n%{http_code}" "$BASE_URL/health" 2>/dev/null || echo "failed\n000")
    status_code=$(echo "$health_response" | tail -n 1)

    if [ "$status_code" != "200" ]; then
        echo -e "${RED}✗ Service is still unhealthy${NC}"
        echo "Please fix the deployment issue before continuing."
        exit 1
    fi

    echo -e "${GREEN}✓ Service is now healthy${NC}"
    SERVICE_HEALTHY=true
else
    echo -e "${RED}✗ Unexpected status: $status_code${NC}"
    SERVICE_HEALTHY=false
fi

echo ""

# Step 3: Apply database migrations
echo -e "${BLUE}Step 3: Applying Database Migrations${NC}"
echo "─────────────────────────────────────────"

echo "Running migrations on Railway..."
echo ""

railway run "python3 run_migrations.py" 2>&1 || {
    echo -e "${YELLOW}⚠ Migration command failed${NC}"
    echo ""
    echo "Try manually:"
    echo "  railway run \"python3 run_migrations.py\""
    echo ""
}

echo ""
echo "Verifying migrations..."

# Test if migrations worked by checking alerts endpoint
alerts_response=$(curl -s "$BASE_URL/api/alerts" 2>/dev/null || echo '{"detail":"failed"}')

if echo "$alerts_response" | grep -q "no such table"; then
    echo -e "${RED}✗ Migrations not applied${NC}"
    echo ""
    echo "The 'alerts' table doesn't exist yet."
    echo ""
    echo "Manual fix:"
    echo "  railway run \"python3 run_migrations.py\""
    echo ""
elif echo "$alerts_response" | grep -q "total"; then
    echo -e "${GREEN}✓ Migrations applied successfully${NC}"
    MIGRATIONS_APPLIED=true
else
    echo -e "${YELLOW}⚠ Cannot verify migrations${NC}"
    echo "Response: $alerts_response"
    MIGRATIONS_APPLIED=false
fi

echo ""

# Step 4: Check environment variables
echo -e "${BLUE}Step 4: Checking Environment Variables${NC}"
echo "─────────────────────────────────────────"

echo "Required environment variables:"
echo ""

# Check which vars are set
VARS_SET=0
VARS_MISSING=0

check_var() {
    local var_name=$1
    local required=$2

    if railway variables list 2>&1 | grep -q "$var_name"; then
        echo -e "  ${GREEN}✓${NC} $var_name"
        ((VARS_SET++))
    else
        if [ "$required" = "true" ]; then
            echo -e "  ${RED}✗${NC} $var_name (required)"
            ((VARS_MISSING++))
        else
            echo -e "  ${YELLOW}⚠${NC} $var_name (optional)"
        fi
    fi
}

check_var "HELIUS_API_KEY" "true"
check_var "BIRDEYE_API_KEY" "true"
check_var "FIRECRAWL_API_KEY" "true"
check_var "TELEGRAM_BOT_TOKEN" "true"
check_var "TELEGRAM_CHAT_ID" "true"
check_var "COINGECKO_API_KEY" "false"

echo ""
echo "Status: $VARS_SET set, $VARS_MISSING missing"

if [ $VARS_MISSING -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}⚠ Missing required environment variables${NC}"
    echo ""
    echo "Set them using:"
    echo "  ./setup_railway_vars.sh"
    echo ""
    echo "Or manually:"
    echo "  railway variables set HELIUS_API_KEY=\"your_key\""
    echo "  railway variables set BIRDEYE_API_KEY=\"your_key\""
    echo "  railway variables set FIRECRAWL_API_KEY=\"your_key\""
    echo "  railway variables set TELEGRAM_BOT_TOKEN=\"your_token\""
    echo "  railway variables set TELEGRAM_CHAT_ID=\"your_chat_id\""
    echo ""
fi

echo ""

# Step 5: Test API endpoints
echo -e "${BLUE}Step 5: Testing API Endpoints${NC}"
echo "─────────────────────────────────────────"

test_endpoint() {
    local name=$1
    local endpoint=$2
    local expected=$3

    echo -n "Testing $name... "

    response=$(curl -s "$BASE_URL$endpoint" 2>/dev/null || echo "failed")

    if echo "$response" | grep -q "$expected"; then
        echo -e "${GREEN}✓${NC}"
        return 0
    else
        echo -e "${RED}✗${NC}"
        echo "  Response: $(echo "$response" | head -c 100)..."
        return 1
    fi
}

ENDPOINTS_OK=0
ENDPOINTS_FAILED=0

test_endpoint "Health" "/health" "status" && ((ENDPOINTS_OK++)) || ((ENDPOINTS_FAILED++))
test_endpoint "Status" "/status" "scanner" && ((ENDPOINTS_OK++)) || ((ENDPOINTS_FAILED++))
test_endpoint "Watchlist" "/api/watchlist" "count" && ((ENDPOINTS_OK++)) || ((ENDPOINTS_FAILED++))
test_endpoint "Alerts" "/api/alerts" "total" && ((ENDPOINTS_OK++)) || ((ENDPOINTS_FAILED++))
test_endpoint "Portfolio" "/api/portfolio" "open_positions" && ((ENDPOINTS_OK++)) || ((ENDPOINTS_FAILED++))

echo ""
echo "Endpoints: $ENDPOINTS_OK OK, $ENDPOINTS_FAILED failed"
echo ""

# Step 6: Summary
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}                       DEPLOYMENT SUMMARY                       ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

if [ "$SERVICE_HEALTHY" = "true" ]; then
    echo -e "Service Health:        ${GREEN}✓ Healthy${NC}"
else
    echo -e "Service Health:        ${RED}✗ Unhealthy${NC}"
fi

if [ "$MIGRATIONS_APPLIED" = "true" ]; then
    echo -e "Database Migrations:   ${GREEN}✓ Applied${NC}"
else
    echo -e "Database Migrations:   ${RED}✗ Not Applied${NC}"
fi

if [ $VARS_MISSING -eq 0 ]; then
    echo -e "Environment Variables: ${GREEN}✓ All Set${NC}"
else
    echo -e "Environment Variables: ${YELLOW}⚠ $VARS_MISSING Missing${NC}"
fi

if [ $ENDPOINTS_FAILED -eq 0 ]; then
    echo -e "API Endpoints:         ${GREEN}✓ All Working${NC}"
else
    echo -e "API Endpoints:         ${YELLOW}⚠ $ENDPOINTS_FAILED Failed${NC}"
fi

echo ""
echo "Deployment URL: $BASE_URL"
echo ""

# Final actions
if [ "$SERVICE_HEALTHY" = "true" ] && [ "$MIGRATIONS_APPLIED" = "true" ] && [ $VARS_MISSING -eq 0 ] && [ $ENDPOINTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║                 ✓ AURA IS FULLY OPERATIONAL ✓                ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Test Telegram bot: Send /start to your bot"
    echo "2. Monitor logs: railway logs --follow"
    echo "3. View dashboard: Open dashboard/app.html in browser"
    echo ""
else
    echo -e "${YELLOW}"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║              ⚠ ACTION REQUIRED TO COMPLETE SETUP ⚠            ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""

    if [ "$SERVICE_HEALTHY" != "true" ]; then
        echo "• Fix Railway deployment (check logs)"
    fi

    if [ "$MIGRATIONS_APPLIED" != "true" ]; then
        echo "• Apply migrations: railway run \"python3 run_migrations.py\""
    fi

    if [ $VARS_MISSING -gt 0 ]; then
        echo "• Set environment variables: ./setup_railway_vars.sh"
    fi

    if [ $ENDPOINTS_FAILED -gt 0 ]; then
        echo "• Fix failing endpoints (check logs for errors)"
    fi

    echo ""
    echo "Then run this script again to verify."
    echo ""
fi

echo "Documentation: SETUP_GUIDE.md"
echo "Support: https://github.com/bydc-cloud/solana-signal-engine/issues"
echo ""
