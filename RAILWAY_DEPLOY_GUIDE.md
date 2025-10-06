# Railway Manual Deployment Guide

## Current Situation
- ✅ All code committed and pushed to GitHub (5 commits, latest: 3bdd147)
- ❌ Railway auto-deploy webhook not triggering
- ❌ New API endpoints returning 404 (old code still running)
- ❌ CODEX fixes not active in production

## How to Manually Deploy in Railway

### Option 1: Railway Web Dashboard (Recommended)

1. **Go to Railway Dashboard**
   - Navigate to: https://railway.app/dashboard
   - Select your project: `solana-signal-engine`

2. **Find Your Service**
   - Click on the service running `api_server.py` and `REALITY_MOMENTUM_SCANNER.py`

3. **Trigger Manual Deploy**
   - Look for **"Deployments"** tab at the top
   - Click **"Deploy"** or **"Redeploy"** button (usually top-right)
   - Select **"Deploy Latest Commit"** from dropdown
   - Confirm deployment

4. **Verify Deployment Started**
   - You should see a new deployment with status "Building" or "Deploying"
   - Watch the logs in real-time as it builds
   - Wait for status to change to "Active" (usually 2-3 minutes)

### Option 2: Railway Settings → GitHub Integration

1. **Check Auto-Deploy Settings**
   - Go to Project Settings → Integrations → GitHub
   - Verify **"Auto Deploy"** is enabled
   - If disabled, enable it and select branch: `main`

2. **Manually Trigger via GitHub**
   - Go to Settings → Deployments
   - Click **"Deploy from GitHub"**
   - Select branch `main` and latest commit `3bdd147`

### Option 3: Railway CLI (If Dashboard Fails)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to your project
cd /Users/johncox/Projects/helix/helix_production
railway link

# Trigger deployment
railway up

# Check deployment status
railway status
```

### Option 4: Force GitHub Webhook Trigger

```bash
# Push a tiny change to force webhook
cd /Users/johncox/Projects/helix/helix_production
git commit --allow-empty -m "chore: trigger Railway webhook manually"
git push origin main
```

## Verify Deployment Success

Once deployment completes, test the new endpoints:

```bash
# Test new endpoints
curl -s https://signal-railway-deployment-production.up.railway.app/tokens/trending | jq .
curl -s https://signal-railway-deployment-production.up.railway.app/wallets | jq .
curl -s https://signal-railway-deployment-production.up.railway.app/positions/active | jq .
curl -s https://signal-railway-deployment-production.up.railway.app/signals/all | jq .

# Check scanner logs for new guard stats format
curl -s https://signal-railway-deployment-production.up.railway.app/logs | grep "guards ->"
```

Expected changes after deployment:
- ✅ `/tokens/trending` returns token data (not 404)
- ✅ Scanner logs show "guards -> holder_count:X, ..." format
- ✅ Micro cap sweep messages appear every 5-10 cycles
- ✅ Some signals with "stale Helius but strong Birdeye" messages

## Troubleshooting

### "I don't see a Deploy button"
- Try refreshing the page
- Check if you're on the "Deployments" tab (not "Settings")
- Look for a **three-dot menu (⋮)** → "Redeploy"
- Try switching to "Service" view vs "Project" view

### "Auto-deploy is enabled but not working"
- Check GitHub → Settings → Webhooks
- Look for Railway webhook URL
- Verify webhook has green checkmark (recent successful delivery)
- If webhook missing or failing, remove and re-add GitHub integration in Railway

### "Deployment started but failed"
- Check build logs in Railway dashboard
- Look for Python dependency errors
- Verify `railway.json` syntax is valid
- Check Railway service logs for startup errors

## What Gets Deployed

When you deploy, Railway will:
1. Pull latest code from GitHub main branch (commit 3bdd147)
2. Install dependencies via Nixpacks
3. Run `init_database.py` to apply migrations
4. Start 5 background processes:
   - `uvicorn api_server:app` (port $PORT)
   - `REALITY_MOMENTUM_SCANNER.py` (scanner)
   - `WALLET_SIGNAL_SCANNER.py` (wallet monitor)
   - `graduation.exit_engine` (exit management)
   - `graduation.twitter_monitor` (social monitoring)

## Expected Impact

After successful deployment:
- **Scanner cycles**: Should find 40+ tokens/cycle (vs current 22)
- **Signal generation**: 1-5 signals/hour (vs current 0)
- **API endpoints**: All 4 new Lovable endpoints working
- **Log format**: Guard rejection stats visible
- **Volume usage**: Log rotation prevents disk fill (max 150MB logs)
