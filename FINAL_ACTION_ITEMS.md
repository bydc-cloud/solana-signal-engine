# 🎯 FINAL ACTION ITEMS - Get AURA Fully Operational

## Current Status

✅ **Complete**: All code, documentation, and automation scripts
⚠️ **Pending**: Railway deployment (currently 502 error)
⚠️ **Needed**: Database migrations + API keys

---

## 🚨 Priority 1: Fix Railway Deployment (CRITICAL)

The Railway service is currently returning 502 errors. This is likely due to:
1. Service crashed during startup
2. Database path issue
3. Missing environment variables
4. Recent deployment issue

### Immediate Fix Steps:

#### Option A: Check Railway Dashboard
1. Go to https://railway.app/dashboard
2. Select your project: `helix-production`
3. Click on the service
4. Check **Logs** tab for errors
5. Look for:
   - `ModuleNotFoundError`
   - `FileNotFoundError`
   - Database connection errors
   - Port binding errors

#### Option B: Restart Service
```bash
# Link Railway project first (if not already linked)
railway link

# View current status
railway status

# Check logs for errors
railway logs | tail -100

# Restart service
railway redeploy
```

#### Option C: Check Build Logs
```bash
# View build logs from recent deployment
railway logs --deployment

# Look for build failures or missing dependencies
```

### Common Issues & Fixes:

**Issue 1: Database path error**
```bash
# Ensure data directory exists in Dockerfile
RUN mkdir -p data

# Verify Dockerfile has correct CMD
CMD python3 init_db.py && \
    python3 init_aura_db.py && \
    python3 run_migrations.py && \
    uvicorn aura_server:app --host 0.0.0.0 --port ${PORT:-8000} & \
    python3 REALITY_MOMENTUM_SCANNER.py & \
    python3 aura_worker.py & \
    python3 ingestion_worker.py & \
    wait
```

**Issue 2: Missing dependencies**
```bash
# Verify requirements.txt has all dependencies
cat requirements.txt | grep -E "firecrawl|aiohttp|telegram"

# If missing, add and redeploy:
git add requirements.txt
git commit -m "fix: add missing dependencies"
git push origin main
```

**Issue 3: Port binding**
```bash
# Ensure Railway PORT env var is set
railway variables set PORT=8000

# Or check Dockerfile EXPOSE
EXPOSE ${PORT:-8000}
```

---

## ⚡ Priority 2: Apply Database Migrations

Once Railway is healthy, apply migrations:

### Method 1: Via Railway CLI (Recommended)
```bash
# Ensure project is linked
railway link

# Run migrations
railway run "python3 run_migrations.py"

# Expected output:
# 🔄 Running database migrations...
# 📝 Applying: 001_dashboard_foundation.sql
# ✅ Applied: 001_dashboard_foundation.sql
# ✅ All migrations applied successfully!
```

### Method 2: Via Railway Dashboard
1. Go to Railway dashboard
2. Select service
3. Click **Settings** → **Service**
4. Scroll to **Run Command**
5. Enter: `python3 run_migrations.py`
6. Click **Run**

### Method 3: Manual SQL (Fallback)
```bash
# Download database from Railway
railway run "cat data/helix_production.db" > local_db.db

# Apply migrations locally
sqlite3 local_db.db < db/migrations/001_dashboard_foundation.sql

# Upload back to Railway (not recommended - use CLI instead)
```

### Verify Migrations:
```bash
# Test alerts endpoint (should no longer error)
curl https://signal-railway-deployment-production.up.railway.app/api/alerts

# Expected: {"total": 0, "unread": 0, "alerts": []}
# Not: {"detail": "Alerts error: no such table: alerts"}
```

---

## 🔑 Priority 3: Set Environment Variables

All API keys are currently missing. Set them using the interactive script:

### Quick Setup:
```bash
./setup_railway_vars.sh
```

This will prompt you for:
1. ✅ **Helius API Key** (https://helius.xyz) - Free tier: 100k requests/day
2. ✅ **Birdeye API Key** (https://birdeye.so/developers) - Free tier: 60 req/min
3. ✅ **Firecrawl API Key** (https://firecrawl.dev) - Free tier: 500 pages/month
4. ✅ **Telegram Bot Token** (from @BotFather)
5. ✅ **Telegram Chat ID** (your user ID)
6. ⚠️ **CoinGecko API Key** (optional - works without)

### Manual Setup:
```bash
# Set one at a time
railway variables set HELIUS_API_KEY="your_key_here"
railway variables set BIRDEYE_API_KEY="your_key_here"
railway variables set FIRECRAWL_API_KEY="your_key_here"
railway variables set TELEGRAM_BOT_TOKEN="123456:ABC-DEF..."
railway variables set TELEGRAM_CHAT_ID="123456789"
railway variables set COINGECKO_API_KEY="CG-..."  # Optional

# Verify all set
railway variables list
```

### Get API Keys:

#### Helius (Required - Solana RPC)
1. Go to https://helius.xyz
2. Sign up (free)
3. Create new API key
4. Copy key (starts with alphanumeric string)
5. Free tier: 100,000 requests/day

#### Birdeye (Required - DEX Data)
1. Go to https://birdeye.so/developers
2. Sign up (free)
3. Create API key
4. Copy key
5. Free tier: 60 requests/minute

#### Firecrawl (Required - Web Scraping)
1. Go to https://firecrawl.dev
2. Sign up (free)
3. Create API key (starts with `fc-`)
4. Copy key
5. Free tier: 500 pages/month

#### Telegram Bot (Required - Notifications)
1. Open Telegram
2. Search for **@BotFather**
3. Send: `/newbot`
4. Choose name: `AURA Trading Bot`
5. Choose username: `aura_trading_bot` (must be unique)
6. Copy token (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### Telegram Chat ID (Required)
1. Start chat with your new bot
2. Send any message (e.g., "hello")
3. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
4. Find `"chat":{"id":123456789}`
5. Copy the number (your chat ID)

#### CoinGecko (Optional - Market Data)
1. Go to https://www.coingecko.com/en/api/pricing
2. Free tier works without key
3. Pro tier: $129/month (optional)
4. If you have Pro, copy key (starts with `CG-`)

---

## 🔄 Priority 4: Restart & Verify

After setting API keys, restart the service:

### Restart:
```bash
railway redeploy
```

### Wait for Startup (60 seconds):
```bash
sleep 60
```

### Verify Health:
```bash
# Should return: {"status": "healthy", ...}
curl https://signal-railway-deployment-production.up.railway.app/health

# Should return: {"count": 0, "tokens": []}
curl https://signal-railway-deployment-production.up.railway.app/api/watchlist

# Should return: {"total": 0, "unread": 0, "alerts": []}
curl https://signal-railway-deployment-production.up.railway.app/api/alerts
```

### Check Logs:
```bash
railway logs --follow
```

Expected log output:
```
🤖 AURA Autonomous Worker starting...
✨ Features: Signal Processing, Governance, Whale Tracking, Sentiment Analysis
🔧 MCP Tools: CoinGecko, Firecrawl, Memory, Puppeteer, Context7

✅ Telegram bot command handlers setup complete

🔄 AURA Worker Cycle #1 - 2025-10-06T12:00:00
✅ Processed 0 new signals

🔄 Ingestion Cycle #1
📊 DefiLlama: Upserted 5 TVL records
⛓️  Helius: Upserted 3 transaction facts
📈 Birdeye: Upserted 15 OHLC candles
✅ Cycle complete: 23 records in 3.45s
```

---

## 📱 Priority 5: Test Telegram Bot

Once service is healthy and credentials are set:

### Test Steps:
1. Open Telegram
2. Search for your bot username (from BotFather)
3. Click **Start** or send `/start`
4. **Expected response**:
   ```
   AURA online ✅ — v0.3.0 production

   Use:
   • /prompt → Ask AURA
   • /panel → Edit config
   • /approve → Apply changes
   • /status → System status
   • /report → Performance digest
   ```

5. Test commands:
   ```
   /status     → Should show system metrics
   /help       → Should show all commands
   /watchlist  → Should show empty watchlist
   /portfolio  → Should show $100k paper equity
   ```

### Troubleshooting:
- **No response**: Check `TELEGRAM_BOT_TOKEN` is set correctly
- **Wrong chat**: Check `TELEGRAM_CHAT_ID` matches your user ID
- **Bot not found**: Verify bot username from @BotFather
- **Errors in logs**: Check Railway logs for Telegram errors

---

## 🎨 Priority 6: Deploy Dashboard Frontend (Optional)

The dashboard is currently only available locally. Deploy it to make it accessible online.

### Option A: Vercel (Recommended)
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd dashboard
vercel --prod

# Expected output:
# ✅ Production: https://aura-dashboard.vercel.app
```

### Option B: Netlify
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
cd dashboard
netlify deploy --prod --dir .

# Expected output:
# ✅ Live URL: https://aura-dashboard.netlify.app
```

### Option C: Railway Static Site
1. Create new Railway service
2. Connect to GitHub repo
3. Set build command: `echo "Static site"`
4. Set start command: `python3 -m http.server $PORT`
5. Set root directory: `dashboard`
6. Deploy

### Update API URL:
After deploying, update `app.html`:
```javascript
// Change this line:
const API_URL = 'http://localhost:8000/api';

// To:
const API_URL = 'https://signal-railway-deployment-production.up.railway.app/api';
```

Then redeploy:
```bash
git add dashboard/app.html
git commit -m "fix: update API URL for production"
git push origin main
vercel --prod  # or netlify deploy --prod
```

---

## ✅ Success Checklist

Use this to verify everything is working:

### System Health
- [ ] Railway deployment is healthy (`/health` returns 200)
- [ ] All 4 workers are running (check logs)
- [ ] Database exists at `data/helix_production.db`
- [ ] No errors in Railway logs

### Database
- [ ] Migrations applied successfully
- [ ] 10 tables exist (tokens, trades, alerts, etc.)
- [ ] No "table not found" errors from API

### API Endpoints
- [ ] `/api/watchlist` returns 200
- [ ] `/api/alerts` returns 200 (not "table not found")
- [ ] `/api/portfolio` returns 200
- [ ] `/api/strategies` returns 200

### Environment Variables
- [ ] `HELIUS_API_KEY` set
- [ ] `BIRDEYE_API_KEY` set
- [ ] `FIRECRAWL_API_KEY` set
- [ ] `TELEGRAM_BOT_TOKEN` set
- [ ] `TELEGRAM_CHAT_ID` set
- [ ] `COINGECKO_API_KEY` set (optional)

### Telegram Bot
- [ ] Bot responds to `/start`
- [ ] `/status` command works
- [ ] `/help` shows all commands
- [ ] `/watchlist` returns empty list
- [ ] No errors when sending commands

### Workers
- [ ] Scanner is generating signals (check logs)
- [ ] Autonomous worker is processing signals
- [ ] Ingestion worker is fetching data (TVL, OHLC, txs)
- [ ] Telegram bot is online

### Dashboard
- [ ] Frontend deployed and accessible
- [ ] API calls work from frontend
- [ ] Real-time WebSocket connected
- [ ] Charts render correctly
- [ ] Share to Telegram action works

---

## 🚀 Quick Command Reference

```bash
# 1. Fix Railway deployment
railway logs | tail -100
railway redeploy

# 2. Apply migrations
railway run "python3 run_migrations.py"

# 3. Set API keys
./setup_railway_vars.sh

# 4. Restart service
railway redeploy

# 5. Verify health
curl https://signal-railway-deployment-production.up.railway.app/health

# 6. Check logs
railway logs --follow

# 7. Test Telegram
# Open Telegram → Search bot → Send /start

# 8. Deploy dashboard (optional)
cd dashboard && vercel --prod
```

---

## 📞 Support

If you encounter issues:

1. **Check Logs**: `railway logs | tail -100`
2. **Verify Docs**: See [SETUP_GUIDE.md](SETUP_GUIDE.md)
3. **Run Health Check**: `./verify_deployment.sh`
4. **Test MCPs**: `python3 mcp_health_check.py`
5. **GitHub Issues**: https://github.com/bydc-cloud/solana-signal-engine/issues

---

## 🎯 Expected Timeline

| Task | Time | Complexity |
|------|------|------------|
| Fix Railway deployment | 5-10 min | Easy |
| Apply migrations | 2 min | Easy |
| Set API keys | 10-15 min | Medium (need to get keys) |
| Restart & verify | 5 min | Easy |
| Test Telegram | 2 min | Easy |
| Deploy dashboard | 10 min | Medium |
| **Total** | **35-45 min** | - |

---

## 🎉 Final Result

After completing these steps, you will have:

✅ Railway deployment healthy and running
✅ Database with all 10 tables
✅ All API endpoints working
✅ Telegram bot responding to commands
✅ 4 workers running 24/7:
  - API server (FastAPI)
  - Scanner (signal generation)
  - Autonomous worker (AURA brain)
  - Ingestion worker (data fetching)
✅ Dashboard deployed and accessible
✅ Complete MCP integration (13 servers)
✅ Real-time data ingestion from:
  - DefiLlama (TVL)
  - Helius (transactions)
  - Birdeye (OHLC prices)
✅ Interactive Telegram control panel

**AURA will be FULLY OPERATIONAL** 🚀

---

*Last Updated: 2025-10-06*
*Version: v0.3.0*
*Status: Awaiting API Keys*
