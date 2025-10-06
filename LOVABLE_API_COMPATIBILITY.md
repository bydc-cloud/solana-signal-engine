# Lovable Dashboard API Compatibility

## Current Railway Deployment Status

**Base URL:** `https://signal-railway-deployment-production.up.railway.app`

---

## ✅ **Working Endpoints (Use These Now)**

### 1. Scanner Status
```bash
GET /status
```
**Returns:**
```json
{
  "scanner_running": true,
  "scanner_status": "running",
  "paper_equity": { "total_usd": 100000, "realized_pnl": 0, "unrealized_pnl": 0 },
  "stats_24h": { "trades": 0, "alerts": 0 },
  "mode": "PAPER"
}
```
**Use For:** Live scanner status indicator

### 2. Scanner Metrics (NEW from CODEX fixes)
```bash
GET /scanner/metrics
```
**Returns:**
```json
{
  "cycles": 0,
  "signals": 0,
  "empty_cycles": 0,
  "last_cycle_seconds": 0,
  "avg_cycle_seconds": 0
}
```
**Use For:** Performance dashboard

### 3. Scanner Logs
```bash
GET /logs
```
**Returns:** Array of recent log messages
**Use For:** Debug panel

---

## ⏳ **Endpoints Referenced in Prompt (Need Implementation)**

These are in the Trading Edge prompt but **not yet implemented** in your backend:

### Token Discovery
```bash
# Need to implement:
GET /tokens/trending?sort=momentum&limit=20
GET /tokens/smartmoney?min_wallets=3&hours=1
GET /tokens/{address}/detail
GET /tokens/{address}/holders
```

### Wallet Intelligence
```bash
# Need to implement:
GET /wallets - List of 20 smart money wallets
GET /wallets/{address} - Wallet details
GET /wallets/activity - Live transaction feed
GET /wallets/{address}/pnl - Multi-timeframe PnL
```

### Signal Performance
```bash
# Need to implement:
GET /signals/all - Historical signals
GET /signals/performance - Win rate stats
GET /signals/confluence - Confluence scores
```

### Position Management
```bash
# Need to implement:
GET /positions/active - Current positions
GET /positions/history - Closed positions
```

### Risk & Analytics
```bash
# Need to implement:
GET /risk/scores - Risk scores for all tokens
GET /analytics/correlation - Token correlation matrix
```

---

## 🎯 **Recommended Lovable Strategy**

### **Phase 1: Use What Works (Now)**
Tell Lovable to build features using **only these endpoints**:
1. **Scanner Status Panel**
   - Use: `GET /status`
   - Show: Running status, paper equity, 24h stats

2. **Scanner Metrics Dashboard**
   - Use: `GET /scanner/metrics`
   - Show: Cycles, signals, timing stats

3. **Live Logs Feed**
   - Use: `GET /logs`
   - Show: Real-time scanner activity

### **Phase 2: Build as You Implement (Later)**
As you add new endpoints to `api_server.py`, add corresponding Lovable features:

1. **Add `/tokens/trending` to backend** → Update Lovable with Token Discovery UI
2. **Add `/wallets` to backend** → Update Lovable with Wallet Intelligence UI
3. **Add `/signals/all` to backend** → Update Lovable with Signal Performance UI

---

## 📝 **Modified Lovable Prompt (Phase 1 Only)**

Instead of the full 10-edge prompt, start with this simplified version:

```markdown
Build a **Solana Trading Intelligence Dashboard** on top of my existing Lovable dashboard.

## API Base URL
`https://signal-railway-deployment-production.up.railway.app`

## Phase 1 Features (Use Current Endpoints)

### 1. Live Scanner Status Panel
**Endpoint:** `GET /status`

Display:
- Scanner status indicator (green dot if running)
- Paper equity: Total USD, realized PnL, unrealized PnL
- 24h stats: Trades count, alerts count
- Trading mode badge (PAPER)

**Design:** Top status bar with cards, auto-refresh every 5s

### 2. Scanner Performance Metrics
**Endpoint:** `GET /scanner/metrics`

Display:
- Total cycles completed
- Total signals generated
- Empty cycles (no signals)
- Average cycle time (seconds)
- Last cycle time (seconds)

**Design:** Grid of metric cards with sparkline charts

### 3. Live Activity Feed
**Endpoint:** `GET /logs`

Display:
- Recent scanner activity (last 20 logs)
- Color-coded by log level (INFO=blue, WARNING=yellow, ERROR=red)
- Auto-scroll to bottom
- Filter by log level

**Design:** Terminal-style log viewer with dark theme

## Tech Stack
- Next.js 14 + React 18 + TypeScript
- TailwindCSS + Shadcn UI
- Tanstack Query (poll every 5s for status/metrics)
- Recharts for sparklines

## Design
- Dark theme (#0a0a0f background)
- Neon accents (green #00ff88, red #ff3366)
- Monospace fonts for numbers
- Glass-morphism cards

Build incrementally. Focus on clean, fast UI.
```

---

## 🚀 **Action Plan**

### **Right Now (Use in Lovable):**
1. ✅ Copy the **simplified Phase 1 prompt** above
2. ✅ Paste into your existing Lovable dashboard
3. ✅ Lovable will add 3 working panels using live data

### **This Week (Backend Work):**
1. Add `/tokens/trending` endpoint to `api_server.py`
2. Add `/wallets` endpoint with your 20 smart money wallets
3. Add `/signals/all` endpoint querying alerts table

### **Next Week (Lovable Updates):**
1. Tell Lovable: "Add Token Discovery panel using GET /tokens/trending"
2. Tell Lovable: "Add Wallet Intelligence using GET /wallets"
3. Continue adding features as you implement backend

---

## 💡 **Why This Approach Works**

**Problem:** Full 10-edge prompt references 30+ endpoints you don't have yet
**Solution:** Build incrementally - 3 panels now, add more as you build backend

**Benefits:**
- ✅ Get working dashboard TODAY
- ✅ No broken API calls
- ✅ Learn Lovable workflow
- ✅ Add features as backend grows

**Timeline:**
- **Today:** 3 working panels
- **Week 1:** Add 3 more features (tokens, wallets, signals)
- **Week 2:** Add advanced features (confluence, dev forensics)
- **Week 3:** Full 10-edge dashboard

---

## 🎯 **Copy This Into Lovable Now**

Use the **Phase 1 simplified prompt** above. It will work with your current Railway deployment.

Then, as you implement new endpoints, come back and add features incrementally.
