# Railway Manual Setup Instructions

## 1. Set Environment Variables

Go to: https://railway.app/project/900cdde4-c62a-4659-a110-fd6151773887/service/0785d30d-a931-47ec-9172-1a01b7adbea8

Click **"Variables"** tab and add these:

### Required API Keys
```
TELEGRAM_BOT_TOKEN=8305979428:AAHoWtmCGgndUZvdrA-vHmnNqyxun53V9_Y
TELEGRAM_CHAT_ID=7024329420
BIRDEYE_API_KEY=21c8998710ad4def9b1d406981e999ea
HELIUS_API_KEY=a059d453-2bd2-49f0-be07-bc96d9a6857f
NASEN_API_KEY=fagAOO6Eu25QOMauRyiYjCKJRWDbrRUY
```

### AI Keys (add ONE of these for Telegram conversations)
```
# Option 1 (preferred):
ANTHROPIC_API_KEY=<your-claude-api-key>

# Option 2 (fallback):
OPENAI_API_KEY=<your-openai-api-key>
```

### Trading Config
```
GRAD_ENABLED=true
GRAD_MODE=PAPER
GRAD_PAPER_START_USD=100000
GRAD_MIN_SCORE=35
GRAD_PER_TRADE_CAP=0.02
GRAD_GLOBAL_EXPOSURE_CAP=0.90
GRAD_MAX_CONCURRENT=20
```

## 2. Import Whale Wallets Database

The file `whale_wallets.sql` contains 9 tracked whale wallets.

### Option A: Railway Shell (recommended)
```bash
# Open Railway shell
railway shell

# Import whale wallets
sqlite3 aura.db < whale_wallets.sql

# Verify
sqlite3 aura.db "SELECT COUNT(*) FROM tracked_wallets WHERE is_active = 1"
```

### Option B: Upload Database
Upload the local `aura.db` file to Railway's persistent volume.

## 3. Start Scanner

### Via Railway Shell:
```bash
railway shell
./start_scanner_railway.sh
```

### Via API:
```bash
curl -X POST https://signal-railway-deployment-production.up.railway.app/api/aura/scanner/start
```

## 4. Test Deployment

Wait 2 minutes after deployment, then run:
```bash
./test_railway_deployment.sh
```

Expected results:
- ✅ Status: Scanner running
- ✅ Signals: 1+ (after scanner runs)
- ✅ Wallets: 9
- ✅ Logs: 50+
- ✅ Social: 4
- ✅ Dashboard: HTTP 200

## 5. Test Telegram Bot

Send any message to your bot:
- "How's my portfolio?"
- "Show me recent signals"
- "What do you think about the market?"

Bot should respond with AI-generated answers using Claude or GPT.

## 6. Verify Dashboard

Open: https://signal-railway-deployment-production.up.railway.app/dashboard

Check all 7 tabs:
1. **Signals** - Should show scanner discoveries
2. **Chat** - Voice AI with auto-silence detection
3. **Wallets** - Should show 9 whale wallets
4. **Portfolio** - Trading positions and P&L
5. **Strategy** - Trading rules and config
6. **Logs** - Real-time system logs
7. **Twitter/X** - Social sentiment trends

---

## Troubleshooting

### Scanner not starting
```bash
railway logs
```
Look for errors in startup.

### Wallets showing 0
Database import didn't work. Manually run:
```bash
railway shell
python3 complete_fixes.py
```

### Telegram bot not responding with AI
Check that ANTHROPIC_API_KEY or OPENAI_API_KEY is set in Railway variables.

### Dashboard not loading
Check deployment status:
```bash
railway status
```

---

## Quick Links

- **Railway Dashboard**: https://railway.app/project/900cdde4-c62a-4659-a110-fd6151773887
- **Live Site**: https://signal-railway-deployment-production.up.railway.app
- **Dashboard**: https://signal-railway-deployment-production.up.railway.app/dashboard
- **API Docs**: https://signal-railway-deployment-production.up.railway.app/docs
