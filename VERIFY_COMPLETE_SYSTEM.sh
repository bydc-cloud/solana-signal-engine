#!/bin/bash
# AURA v0.3.0 - Complete System Verification
# Tests all components end-to-end

echo "🔍 AURA v0.3.0 - Complete System Verification"
echo "=============================================="
echo ""

BASE_URL="https://signal-railway-deployment-production.up.railway.app"
PASS=0
FAIL=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

test_endpoint() {
    local name="$1"
    local endpoint="$2"
    local expected_status="${3:-200}"

    echo -n "Testing $name... "

    response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$endpoint" 2>/dev/null)

    if [ "$response" == "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $response)"
        ((PASS++))
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $response, expected $expected_status)"
        ((FAIL++))
    fi
}

test_endpoint_with_data() {
    local name="$1"
    local endpoint="$2"
    local pattern="$3"

    echo -n "Testing $name... "

    response=$(curl -s "$BASE_URL$endpoint" 2>/dev/null)

    if echo "$response" | grep -q "$pattern"; then
        echo -e "${GREEN}✓ PASS${NC} (Found: $pattern)"
        ((PASS++))
    else
        echo -e "${RED}✗ FAIL${NC} (Pattern not found: $pattern)"
        echo "  Response: ${response:0:100}..."
        ((FAIL++))
    fi
}

echo -e "${BLUE}📡 Core Endpoints${NC}"
echo "--------------------"
test_endpoint "Dashboard" "/" 200
test_endpoint "Health Status" "/status" 200
test_endpoint "API Docs" "/docs" 200

echo ""
echo -e "${BLUE}🔍 Scanner Endpoints${NC}"
echo "--------------------"
test_endpoint_with_data "Recent Signals" "/api/aura/scanner/signals" "signals"
test_endpoint_with_data "Scanner Metrics" "/api/aura/scanner/metrics" "cycles"
test_endpoint_with_data "Scanner Tiers" "/api/aura/scanner/tiers" "tier"

echo ""
echo -e "${BLUE}🐋 Wallet Tracking${NC}"
echo "--------------------"
test_endpoint_with_data "Tracked Wallets" "/api/aura/wallets" "wallets"

echo ""
echo -e "${BLUE}💼 Portfolio Endpoints${NC}"
echo "--------------------"
test_endpoint_with_data "Portfolio Summary" "/api/aura/portfolio/summary" "open_positions"
test_endpoint_with_data "Portfolio Positions" "/api/aura/portfolio/positions" "positions"

echo ""
echo -e "${BLUE}👁️  Watchlist Endpoints${NC}"
echo "--------------------"
test_endpoint_with_data "Watchlist" "/api/aura/watchlist" "items"

echo ""
echo -e "${BLUE}💬 Chat System${NC}"
echo "--------------------"
echo -n "Testing MCP Chat... "
chat_response=$(curl -s -X POST "$BASE_URL/api/aura/chat" \
    -H "Content-Type: application/json" \
    -d '{"query":"What are the latest signals?"}' 2>/dev/null)

if echo "$chat_response" | grep -q "message"; then
    echo -e "${GREEN}✓ PASS${NC} (Got response)"
    ((PASS++))
else
    echo -e "${RED}✗ FAIL${NC} (No message in response)"
    echo "  Response: ${chat_response:0:100}..."
    ((FAIL++))
fi

echo ""
echo -e "${BLUE}📊 Data Validation${NC}"
echo "--------------------"

# Check if signals have proper structure
echo -n "Validating signal structure... "
signal_data=$(curl -s "$BASE_URL/api/aura/scanner/signals" 2>/dev/null)
if echo "$signal_data" | grep -q "momentum_score"; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASS++))
else
    echo -e "${RED}✗ FAIL${NC} (Missing momentum_score)"
    ((FAIL++))
fi

# Check if wallets have proper structure
echo -n "Validating wallet structure... "
wallet_data=$(curl -s "$BASE_URL/api/aura/wallets" 2>/dev/null)
if echo "$wallet_data" | grep -q "win_rate"; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASS++))
else
    echo -e "${RED}✗ FAIL${NC} (Missing win_rate)"
    ((FAIL++))
fi

echo ""
echo "=============================================="
echo -e "Test Results: ${GREEN}$PASS passed${NC}, ${RED}$FAIL failed${NC}"
echo "=============================================="

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo ""
    echo "✅ System Status: FULLY OPERATIONAL"
    echo "✅ Dashboard: $BASE_URL"
    echo "✅ API: Working"
    echo "✅ Scanner: Generating signals"
    echo "✅ Chat: MCP-powered"
    echo "✅ Wallets: Tracked"
    echo ""
    exit 0
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo ""
    echo "Check Railway logs: railway logs"
    echo "Check service status: $BASE_URL/status"
    echo ""
    exit 1
fi
