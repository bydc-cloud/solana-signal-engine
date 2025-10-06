# Railway CLI Deployment Steps

## ✅ Railway CLI Installed Successfully
Version: railway 4.10.0
Location: /Users/johncox/.nvm/versions/node/v20.19.3/bin/railway

---

## Next Steps to Deploy

### Step 1: Login to Railway
Run this command - it will open your browser for authentication:
```bash
railway login
```

**What happens:**
1. Browser opens to Railway login page
2. You authorize the CLI
3. Browser shows "Success! You can close this window"
4. Terminal shows "Logged in as [your email]"

---

### Step 2: Link to Your Project
Navigate to the project directory and link:
```bash
cd /Users/johncox/Projects/helix/helix_production
railway link
```

**What you'll be prompted for:**
1. **Select team/account** → Choose your Railway account
2. **Select project** → Choose "solana-signal-engine" (or similar name)
3. **Select service** → Choose your main API/scanner service

**Expected output:**
```
🎉 Linked to project: solana-signal-engine
   Service: [your-service-name]
```

---

### Step 3: Deploy Your Code
Once linked, deploy:
```bash
railway up
```

**What happens:**
1. CLI uploads your code to Railway
2. Railway builds using your Dockerfile
3. Deployment starts automatically
4. Terminal shows build logs in real-time

**Expected output:**
```
🚀 Deploying...
Building with Dockerfile...
Step 1/10 : FROM python:3.11-slim
...
✅ Deployment live
```

---

## Alternative Commands

### Check Current Status
```bash
railway status
```

### View Live Logs
```bash
railway logs
```

### Redeploy Without Changes
```bash
railway redeploy
```

### Open Railway Dashboard
```bash
railway open
```

---

## If You Get Errors

### "Not authenticated"
Run: `railway login`

### "No project linked"
Run: `railway link` and select your project

### "Multiple services found"
Run: `railway service` to select which service to deploy

### "Build failed"
Check logs: `railway logs`
Most common: Missing environment variables

---

## After Successful Deployment

Test the new endpoints:
```bash
# Should work now (not 404)
curl -s https://signal-railway-deployment-production.up.railway.app/tokens/trending

# Check for guard stats in logs
curl -s https://signal-railway-deployment-production.up.railway.app/logs | grep "guards ->"

# Check for micro cap sweep messages
curl -s https://signal-railway-deployment-production.up.railway.app/logs | grep "Triggering micro cap sweep"
```

---

## Ready to Start?

Run these commands in order:
```bash
railway login
cd /Users/johncox/Projects/helix/helix_production
railway link
railway up
```

This will authenticate, link to your project, and deploy all 7 pending commits with CODEX fixes!
