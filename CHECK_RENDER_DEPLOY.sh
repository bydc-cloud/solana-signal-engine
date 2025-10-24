#!/bin/bash
# Monitor Render deployment status

echo "🔍 Checking Render deployment status..."
echo ""

# Check if v2 endpoint exists (new code)
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://helix-trading-bot.onrender.com/api/aura/wallets/v2)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ NEW CODE DEPLOYED! v2 endpoint is live"
    echo ""
    echo "Run these commands to activate:"
    echo "1. curl -s https://helix-trading-bot.onrender.com/api/aura/init"
    echo "2. curl -s https://helix-trading-bot.onrender.com/api/aura/load_trackers"
    echo "3. curl -X POST https://helix-trading-bot.onrender.com/api/aura/track_whales_live"
    echo ""
    echo "Then visit: https://helix-trading-bot.onrender.com/dashboard/aura-complete.html"
elif [ "$HTTP_CODE" = "404" ]; then
    echo "⏳ OLD CODE STILL RUNNING (v2 endpoint returns 404)"
    echo ""
    echo "Options:"
    echo "1. Manually trigger deploy at: https://dashboard.render.com/"
    echo "2. Wait for auto-deploy (can take 5-15 minutes)"
    echo "3. Use local version at: http://localhost:8001/dashboard/aura-complete.html"
else
    echo "❌ Unexpected response: HTTP $HTTP_CODE"
fi

echo ""
echo "Health check: $(curl -s https://helix-trading-bot.onrender.com/health | python3 -m json.tool 2>&1 | head -1)"
