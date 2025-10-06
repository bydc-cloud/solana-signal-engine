# 🚀 AURA Setup Guide - Complete Bot Configuration

## Prerequisites
- Railway account with deployed service
- API keys for: Helius, Birdeye, Firecrawl, CoinGecko (optional), Telegram Bot

---

## Step 1: Apply Database Migrations

### Option A: Via Railway Dashboard (Easiest)
1. Go to https://railway.app/dashboard
2. Select your project: `helix-production`
3. Click on the service
4. Go to **Settings** → **Deployments**
5. Click **"Run Command"** or **"Console"**
6. Run:
   ```bash
   python3 run_migrations.py
   ```
7. Verify output shows: `✅ All migrations applied successfully!`

### Option B: Via Railway CLI
```bash
# Link project (interactive)
railway link

# Apply migrations
railway run "python3 run_migrations.py"
```

### Option C: Via API (Automated)
```bash
# Use the provided script
./railway_apply_migrations.sh
```

---

## Step 2: Set Environment Variables

### Required API Keys

#### 1. Helius (Solana RPC)
- **Get Key**: https://helius.xyz/ (Free tier: 100k requests/day)
- **Set in Railway**:
  ```bash
  railway variables set HELIUS_API_KEY="your_helius_key_here"
  ```

#### 2. Birdeye (DEX Data)
- **Get Key**: https://birdeye.so/developers (Free tier: 60 requests/min)
- **Set in Railway**:
  ```bash
  railway variables set BIRDEYE_API_KEY="your_birdeye_key_here"
  ```

#### 3. Firecrawl (Web Scraping)
- **Get Key**: https://firecrawl.dev/ (Free tier: 500 pages/month)
- **Set in Railway**:
  ```bash
  railway variables set FIRECRAWL_API_KEY="your_firecrawl_key_here"
  ```

#### 4. Telegram Bot (Notifications)
- **Get Token**: Talk to [@BotFather](https://t.me/botfather) on Telegram
  - Send `/newbot`
  - Choose name and username
  - Copy the token
- **Get Chat ID**:
  - Start chat with your bot
  - Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
  - Copy the `chat.id` value
- **Set in Railway**:
  ```bash
  railway variables set TELEGRAM_BOT_TOKEN="your_bot_token_here"
  railway variables set TELEGRAM_CHAT_ID="your_chat_id_here"
  ```

#### 5. CoinGecko (Market Data - Optional)
- **Get Key**: https://www.coingecko.com/en/api/pricing (Optional - works without)
- **Set in Railway**:
  ```bash
  railway variables set COINGECKO_API_KEY="your_coingecko_key_here"
  ```

### Quick Setup Script
```bash
# Create a .env file with your keys
cat > railway_env_vars.txt <<EOF
HELIUS_API_KEY=your_helius_key
BIRDEYE_API_KEY=your_birdeye_key
FIRECRAWL_API_KEY=your_firecrawl_key
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
COINGECKO_API_KEY=your_coingecko_key
EOF

# Apply all at once
while IFS='=' read -r key value; do
  railway variables set "$key=$value"
done < railway_env_vars.txt
```

---

## Step 3: Verify Deployment

### Check System Health
```bash
curl https://signal-railway-deployment-production.up.railway.app/health
```

**Expected Output**:
```json
{
  "status": "healthy",
  "helix": {"scanner_running": false, "database_initialized": true},
  "aura": {"status": "healthy", "tokens_tracked": 0}
}
```

### Check Dashboard API Endpoints
```bash
# Watchlist
curl https://signal-railway-deployment-production.up.railway.app/api/watchlist

# Alerts (after migrations)
curl https://signal-railway-deployment-production.up.railway.app/api/alerts

# Portfolio
curl https://signal-railway-deployment-production.up.railway.app/api/portfolio
```

### Check Scanner Logs
```bash
curl https://signal-railway-deployment-production.up.railway.app/logs
```

---

## Step 4: Test Telegram Bot

### Start Telegram Bot
1. Open Telegram
2. Search for your bot username (from BotFather)
3. Send `/start`
4. Try commands:
   - `/status` - System status
   - `/help` - Show all commands
   - `/watchlist` - View watchlist
   - `/signals` - Recent signals

### Available Commands
| Command | Description |
|---------|-------------|
| `/status` | System status and metrics |
| `/portfolio` | Portfolio summary with P&L |
| `/watchlist` | Show tracked tokens |
| `/signals` | Recent signals (24h) |
| `/strategies` | Active trading strategies |
| `/scan` | Trigger manual scanner cycle |
| `/report today` | Performance report (today) |
| `/report week` | Performance report (week) |
| `/prompt [text]` | Send prompt to AURA |
| `/panel edit [key] [value]` | Propose config change |
| `/approve [id]` | Apply pending config patch |
| `/help` | Show help |

---

## Step 5: Monitor Workers

### Check Worker Status
All 4 processes should be running:
1. **aura_server** (FastAPI) - Port 8000
2. **REALITY_MOMENTUM_SCANNER** - Signal generation
3. **aura_worker** - Autonomous actions
4. **ingestion_worker** - Data fetching

### View Logs
```bash
# Railway CLI
railway logs

# Or via dashboard
# Go to: https://railway.app/dashboard → Your Project → Logs
```

### Expected Log Output
```
🤖 AURA Autonomous Worker starting...
✨ Features: Signal Processing, Governance, Whale Tracking, Sentiment Analysis
🔧 MCP Tools: CoinGecko, Firecrawl, Memory, Puppeteer, Context7

🔄 AURA Worker Cycle #1 - 2025-10-06T20:00:00
✅ Processed 0 new signals

🔄 Ingestion Cycle #1
📊 DefiLlama: Upserted 5 TVL records
⛓️  Helius: Upserted 3 transaction facts
📈 Birdeye: Upserted 15 OHLC candles
✅ Cycle complete: 23 records in 3.45s
```

---

## Step 6: Deploy Dashboard (Optional)

### Option A: Vercel Deployment
1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Deploy dashboard:
   ```bash
   cd dashboard
   vercel --prod
   ```

3. Configure API endpoint:
   - Edit `app.html`
   - Change `API_URL` to: `https://signal-railway-deployment-production.up.railway.app/api`

### Option B: Netlify Deployment
1. Install Netlify CLI:
   ```bash
   npm install -g netlify-cli
   ```

2. Deploy:
   ```bash
   cd dashboard
   netlify deploy --prod --dir .
   ```

### Option C: Static File Server
1. Serve locally:
   ```bash
   cd dashboard
   python3 -m http.server 8888
   ```

2. Open: http://localhost:8888/app.html

---

## Step 7: Test MCP Tools

### Run Health Check
```bash
python3 mcp_health_check.py
```

**Expected Output**:
- ✅ memory (local)
- ✅ puppeteer (local)
- ✅ sequential-thinking (local)
- ✅ repo (local)
- ⚠️ HTTP MCPs (404) - Need implementation

### Test CoinGecko MCP
```python
from aura.mcp_toolkit import get_token_price, get_trending_tokens
import asyncio

# Get SOL price
price = asyncio.run(get_token_price("solana"))
print(f"SOL Price: ${price}")

# Get trending tokens
trending = asyncio.run(get_trending_tokens())
print(f"Trending: {trending[:3]}")
```

---

## Troubleshooting

### Issue: "No signals generated"
**Solution**:
1. Check scanner is running: `curl .../status`
2. Verify Helius API key is set
3. Check logs for errors: `railway logs`
4. Lower signal thresholds in config

### Issue: "Telegram bot not responding"
**Solution**:
1. Verify `TELEGRAM_BOT_TOKEN` is set
2. Verify `TELEGRAM_CHAT_ID` is correct
3. Check bot is running: `railway logs | grep Telegram`
4. Test webhook: `curl https://api.telegram.org/bot<TOKEN>/getMe`

### Issue: "Dashboard shows 'API Error'"
**Solution**:
1. Check API is responding: `curl .../health`
2. Check CORS settings in `aura_server.py`
3. Verify Railway deployment is healthy
4. Check browser console for errors

### Issue: "Ingestion workers not fetching data"
**Solution**:
1. Verify API keys are set: `railway variables list`
2. Check logs: `railway logs | grep Ingestion`
3. Verify watchlist has tokens: `curl .../api/watchlist`
4. Check API rate limits

### Issue: "Migrations not applied"
**Solution**:
1. Run manually: `railway run "python3 run_migrations.py"`
2. Check database exists: `ls data/helix_production.db`
3. Verify migrations file: `cat db/migrations/001_dashboard_foundation.sql`
4. Check logs for migration errors

---

## Verification Checklist

Use this checklist to verify everything is working:

- [ ] Railway deployment is healthy (`/health` returns 200)
- [ ] Database migrations applied (no "table not found" errors)
- [ ] Scanner is running (check logs)
- [ ] Autonomous worker is running (check logs)
- [ ] Ingestion worker is running (check logs)
- [ ] Telegram bot responds to `/start`
- [ ] Telegram commands work (`/status`, `/help`)
- [ ] Dashboard API endpoints return data
- [ ] Watchlist can be viewed (`/api/watchlist`)
- [ ] Alerts system works (`/api/alerts`)
- [ ] MCP toolkit is available (check worker logs)
- [ ] CoinGecko MCP enrichment working (check token facts)
- [ ] Firecrawl MCP scraping working (check token facts)
- [ ] Memory MCP storing entities (check logs)

---

## Quick Start Commands

```bash
# 1. Apply migrations
railway run "python3 run_migrations.py"

# 2. Set API keys (replace with your keys)
railway variables set HELIUS_API_KEY="..."
railway variables set BIRDEYE_API_KEY="..."
railway variables set FIRECRAWL_API_KEY="..."
railway variables set TELEGRAM_BOT_TOKEN="..."
railway variables set TELEGRAM_CHAT_ID="..."

# 3. Restart service
railway redeploy

# 4. Verify health
curl https://signal-railway-deployment-production.up.railway.app/health

# 5. Test Telegram bot
# Open Telegram and send /start to your bot

# 6. Check logs
railway logs --follow
```

---

## Next Steps

1. ✅ Complete this setup guide
2. Monitor scanner for signals (should generate 3-10 per cycle)
3. Review Telegram alerts as they come in
4. Adjust signal thresholds based on results
5. Deploy dashboard frontend to Vercel/Netlify
6. Implement HTTP MCP server endpoints (optional)
7. Add custom trading strategies
8. Configure alert rules
9. Set up portfolio tracking

---

## Support

- **Documentation**: See [MCP_ARCHITECTURE_COMPLETE.md](MCP_ARCHITECTURE_COMPLETE.md)
- **Ingestion Plan**: See [WORKER_INGESTION_PLAN.md](WORKER_INGESTION_PLAN.md)
- **MCP Config**: See [mcp_config.json](mcp_config.json)
- **GitHub Issues**: https://github.com/bydc-cloud/solana-signal-engine/issues

---

*Last Updated: 2025-10-06*
*AURA v0.3.0*
