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
