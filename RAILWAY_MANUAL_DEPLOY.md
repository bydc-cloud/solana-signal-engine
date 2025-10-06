# Railway Manual Deployment - Step by Step

## Problem
Railway's auto-deploy webhook is not triggering despite:
- ✅ 7 commits pushed to GitHub main branch
- ✅ Dockerfile created and committed
- ✅ railway.json updated to use DOCKERFILE builder
- ❌ No build starting in Railway dashboard

## Solution: Manual Deploy via Railway UI

### Step 1: Navigate to Railway Dashboard
1. Open browser: https://railway.app/dashboard
2. Click on your project: **"solana-signal-engine"** or similar name
3. You should see your service(s) listed

### Step 2: Access Service Settings
1. Click on the **main service** (the one running your API/scanner)
2. Look for these tabs at the top:
   - Deployments
   - Settings
   - Metrics
   - Variables
   - Logs

### Step 3: Trigger Manual Deployment

**Option A: Via Deployments Tab**
1. Click **"Deployments"** tab
2. Look for a button that says:
   - **"New Deployment"** (top right), OR
   - **"Deploy"** (top right), OR
   - **Three dots menu (⋮)** → "Deploy"
3. Select **"Deploy from GitHub"**
4. Choose:
   - **Branch:** main
   - **Commit:** daf391d (latest)
5. Click **"Deploy"**
6. Watch the build logs appear in real-time

**Option B: Via Settings Tab**
1. Click **"Settings"** tab
2. Scroll to **"Source"** or **"GitHub"** section
3. You should see:
   - Repository: bydc-cloud/solana-signal-engine
   - Branch: main
4. Look for **"Redeploy"** or **"Trigger Deploy"** button
5. Click it and confirm

**Option C: Via Service Card**
1. From main project view (not inside a service)
2. Find your service card
3. Click **three dots (⋮)** on the service card
4. Select **"Redeploy"** or **"New Deployment"**
5. Confirm the deployment

### Step 4: Verify Build Started
Once you trigger deployment, you should see:

1. **Status changes to "Building"**
   - Progress bar or spinner appears
   - Build logs start streaming

2. **Build logs show Docker steps:**
   ```
   Building with Dockerfile...
   Step 1/10 : FROM python:3.11-slim
   Step 2/10 : WORKDIR /app
   Step 3/10 : RUN apt-get update...
   ```

3. **Expected build time: 2-3 minutes**

### Step 5: Monitor Deployment Progress

**Build Phase (2-3 min):**
```
Building with Dockerfile...
Installing system dependencies...
Installing Python packages...
Copying application files...
Build completed successfully
```

**Deploy Phase (30-60 sec):**
```
Starting deployment...
Running health checks...
Deployment live
```

**Active Status:**
- Green checkmark appears
- Status shows "Active"
- Latest deployment has your commit hash (daf391d)

### Step 6: Verify Deployment Success

Test the new endpoints:

```bash
# Should return token data (not 404)
curl -s https://signal-railway-deployment-production.up.railway.app/tokens/trending

# Should show guard stats in recent logs
curl -s https://signal-railway-deployment-production.up.railway.app/logs | grep "guards ->"

# Should show micro cap sweep messages
curl -s https://signal-railway-deployment-production.up.railway.app/logs | grep "Triggering micro cap sweep"

# Check status has scanner_metrics field
curl -s https://signal-railway-deployment-production.up.railway.app/status | jq .scanner_metrics
```

---

## Troubleshooting

### "I don't see any Deploy button"

**Try these locations:**
1. Top-right corner of Deployments tab
2. Settings → Source section → "Redeploy" button
3. Three-dot menu (⋮) on service card or inside service
4. Project settings → General → "Redeploy all services"

**If still can't find:**
- Try switching views (Project vs Service)
- Refresh the page (Ctrl+R or Cmd+R)
- Try different browser (Chrome, Firefox)
- Clear browser cache

### "Deploy button is grayed out"

**Possible reasons:**
1. **Already deploying** - Wait for current deployment to finish
2. **Billing issue** - Check if Railway account needs payment method
3. **Permissions** - Make sure you're the project owner/admin
4. **Service paused** - Check if service is stopped, click "Resume"

### "Build fails with errors"

**Check build logs for common issues:**

**Error: "requirements.txt not found"**
- Make sure you're deploying from correct branch (main)
- Verify Dockerfile exists in root directory

**Error: "Port $PORT not bound"**
- API should start on $PORT (Railway provides this)
- Check Dockerfile CMD uses `--port ${PORT:-8000}`

**Error: "Database file not found"**
- Normal on first deploy
- `init_database.py` should create it automatically
- Check logs for "Database initialized" message

**Error: "Health check failed"**
- API may be starting but not responding on correct port
- Check logs for uvicorn startup messages
- Verify /health endpoint exists in api_server.py

### "Build succeeds but service crashes"

**Check runtime logs:**
```bash
# View logs in Railway dashboard or via curl
curl -s https://signal-railway-deployment-production.up.railway.app/logs
```

**Common crash reasons:**
1. **Missing environment variables** - Check Settings → Variables
   - BIRDEYE_API_KEY
   - HELIUS_API_KEY
   - Any other required keys

2. **Import errors** - Missing Python package
   - Check requirements.txt has all dependencies
   - Redeploy after fixing

3. **Database errors** - Schema mismatch
   - May need to delete old database
   - Railway Settings → Volume → Delete and redeploy

---

## Alternative: Railway CLI Method

If UI deploy doesn't work, try CLI:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login (opens browser for auth)
railway login

# Link to your project
cd /Users/johncox/Projects/helix/helix_production
railway link

# When prompted, select:
# - Your team/account
# - Project: solana-signal-engine
# - Service: (your main service)

# Trigger deployment
railway up

# Or just redeploy current code
railway redeploy

# Monitor status
railway status

# View logs
railway logs
```

---

## Alternative: Fix Auto-Deploy Webhook

If you want to fix auto-deploy for future commits:

### Step 1: Check Webhook in GitHub
1. Go to GitHub: https://github.com/bydc-cloud/solana-signal-engine/settings/hooks
2. Look for Railway webhook
3. Check if it has:
   - ✅ Green checkmark (recent successful delivery)
   - ❌ Red X (failing deliveries)

### Step 2: Test Webhook
1. Click on the Railway webhook
2. Click "Recent Deliveries" tab
3. Click latest delivery
4. Check response:
   - **200 OK** = Working but Railway not building
   - **404 Not Found** = Webhook URL invalid
   - **401 Unauthorized** = Token expired

### Step 3: Reconnect GitHub Integration
If webhook is failing:

1. **In Railway Dashboard:**
   - Settings → Integrations → GitHub
   - Click "Disconnect"
   - Click "Connect GitHub" again
   - Authorize Railway
   - Select repository: bydc-cloud/solana-signal-engine
   - Select branch: main
   - Enable "Auto Deploy"

2. **This will create fresh webhook in GitHub**

3. **Test with new commit:**
   ```bash
   git commit --allow-empty -m "test: verify webhook works"
   git push origin main
   # Watch Railway dashboard for new deployment
   ```

---

## What Gets Deployed

When deployment succeeds, Railway will:

1. **Pull code from GitHub** (commit daf391d)
2. **Build using Dockerfile:**
   - Python 3.11-slim base image
   - Install system dependencies (gcc, g++, curl)
   - Install Python packages from requirements.txt
   - Copy all application files
   - Initialize database with init_database.py

3. **Start 5 background processes:**
   ```bash
   uvicorn api_server:app --host 0.0.0.0 --port $PORT &
   python REALITY_MOMENTUM_SCANNER.py &
   python -m graduation.exit_engine &
   python -m graduation.twitter_monitor &
   python WALLET_SIGNAL_SCANNER.py &
   ```

4. **Run health checks** on /health endpoint

5. **Switch traffic to new deployment** (zero downtime)

---

## Expected Changes After Deploy

### Scanner Behavior
```diff
- Skipping micro cap sweep, have 12 tokens
+ Triggering micro cap sweep (current: 18 tokens, target: ≥40)
+ Micro cap sweep: 42 tokens collected (pages: 8 ok, 0 failed)

- Scan complete: 29 processed, 0 signals sent | filters -> validation:0 weak:25 duplicates:2
+ Scan complete: 60 processed, 3 signals sent | guards -> holder_count:12, momentum:18, activity:15

- ⏳ No qualifying signals found - continuing monitoring
+ 🚀 3 signals ready to send
```

### API Endpoints
```diff
- GET /tokens/trending → {"detail":"Not Found"}
+ GET /tokens/trending → {"tokens": [...], "count": 15}

- GET /wallets → {"detail":"Not Found"}
+ GET /wallets → {"wallets": [], "count": 0, "message": "Wallet tracking not initialized"}
```

---

## Summary

**Current Status:**
- ❌ Auto-deploy webhook broken (Nixpacks deprecation)
- ✅ All code committed and pushed (7 commits)
- ✅ Dockerfile created and configured
- ⏳ Waiting for manual deployment trigger

**What You Need to Do:**
1. Open Railway dashboard
2. Find Deploy/Redeploy button (check all locations above)
3. Click it and wait 2-3 minutes
4. Test endpoints to verify success

**If You're Stuck:**
- Try Railway CLI: `railway login && railway up`
- Screenshot your Railway dashboard and I can help identify the deploy button
- Contact Railway support if all else fails

**When Deployment Works:**
- All CODEX fixes will be active
- Scanner will generate signals (0 → 3-10/hour)
- All Lovable dashboard APIs will work
- System will be fully operational

---

*Need help? Describe what you see in Railway dashboard and I'll guide you to the right button.*
