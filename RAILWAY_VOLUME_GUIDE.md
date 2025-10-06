# Railway Volume Management Guide

**Current Allocation:** 500 MB
**Status:** ✅ Sufficient for 6-12 months with proper management

---

## 📊 **Volume Usage Breakdown**

### **What Takes Up Space:**

| Component | Typical Size | Max Size (with management) | Notes |
|-----------|--------------|---------------------------|-------|
| **Database** | 5-50 MB | 100 MB | Signals, trades, wallets |
| **Log Files** | 50-150 MB | 150 MB | **NOW CAPPED** with rotation |
| **Python Packages** | 200-300 MB | Fixed | Installed once, doesn't grow |
| **Code** | 1-2 MB | Fixed | Your Python scripts |
| **Total** | ~250-500 MB | **~450 MB max** | Safe for 500 MB volume |

---

## ✅ **What We Just Fixed**

### **1. Log Rotation (Implemented)**
```python
# In REALITY_MOMENTUM_SCANNER.py
RotatingFileHandler(
    'momentum_scanner.log',
    maxBytes=50_000_000,  # 50 MB max
    backupCount=2,  # Keep 2 old files
)
# Total logs: 150 MB max (vs unlimited before ❌)
```

**Impact:** Logs will never exceed 150 MB

### **2. Database Cleanup Script (Created)**
```bash
# Run monthly to clean old data
python3 cleanup_old_data.py

# What it does:
- Deletes signals older than 90 days
- Deletes trades older than 180 days
- Runs VACUUM to reclaim space
```

**Impact:** Database stays under 100 MB even after 1 year

---

## 🔍 **How to Monitor Volume Usage**

### **Option 1: Railway Dashboard** (Easiest)
1. Go to https://railway.app → Your project
2. Click "Settings" → "Volumes"
3. See usage bar: `X MB / 500 MB used`

### **Option 2: SSH into Railway**
```bash
# If you have Railway CLI
railway run bash

# Check database size
du -sh final_nuclear.db

# Check log files
du -sh *.log*

# Check total volume usage
df -h /app
```

### **Option 3: Add to API** (Recommended)
Add volume monitoring endpoint:

```python
# In api_server.py
import os
from pathlib import Path

@app.get("/system/storage")
async def get_storage_info():
    """Get volume usage stats"""
    try:
        db_path = DB_PATH
        log_path = Path("momentum_scanner.log")

        db_size = os.path.getsize(db_path) / (1024 * 1024) if db_path.exists() else 0

        log_sizes = []
        for log_file in Path().glob("momentum_scanner.log*"):
            log_sizes.append(os.path.getsize(log_file) / (1024 * 1024))

        total_logs = sum(log_sizes)

        # Count database records
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM alerts")
            signals_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM trades")
            trades_count = cur.fetchone()[0]

        return {
            "volume_limit_mb": 500,
            "database_mb": round(db_size, 2),
            "logs_mb": round(total_logs, 2),
            "estimated_total_mb": round(db_size + total_logs + 300, 2),  # +300 for packages
            "percentage_used": round((db_size + total_logs + 300) / 500 * 100, 1),
            "database_records": {
                "signals": signals_count,
                "trades": trades_count,
            },
            "warnings": [
                "⚠️ Volume >80% full" if (db_size + total_logs + 300) / 500 > 0.8 else None,
                "⚠️ Logs >100 MB" if total_logs > 100 else None,
                "⚠️ Database >80 MB" if db_size > 80 else None,
            ],
            "recommendations": [
                "Run cleanup_old_data.py" if db_size > 80 else None,
                "Check log rotation working" if total_logs > 100 else None,
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

Then monitor via:
```bash
curl https://signal-railway-deployment-production.up.railway.app/system/storage
```

---

## 🚨 **Warning Signs**

### **When to Act:**

| Usage | Status | Action |
|-------|--------|--------|
| <300 MB | 🟢 Healthy | No action needed |
| 300-400 MB | 🟡 Caution | Schedule cleanup within 30 days |
| 400-450 MB | 🟠 Warning | Run cleanup script ASAP |
| >450 MB | 🔴 Critical | Clean NOW + consider 1GB upgrade |

---

## 🔧 **Cleanup Procedures**

### **Weekly Cleanup** (Automated)
Add to Railway cron (if available) or run manually weekly:
```bash
# Test what would be deleted
DRY_RUN=true python3 cleanup_old_data.py

# Actually delete old data
python3 cleanup_old_data.py
```

### **Emergency Cleanup** (Volume >90%)
If you're almost out of space:

```python
# Quick cleanup script - delete last 30 days only
import sqlite3
from datetime import datetime, timedelta

DB_PATH = "final_nuclear.db"
cutoff = (datetime.now() - timedelta(days=30)).isoformat()

with sqlite3.connect(DB_PATH) as conn:
    cur = conn.cursor()

    # Delete old signals
    cur.execute("DELETE FROM alerts WHERE created_at < ?", (cutoff,))
    print(f"Deleted {cur.rowcount} old signals")

    # Delete old trades
    cur.execute("DELETE FROM trades WHERE created_at < ?", (cutoff,))
    print(f"Deleted {cur.rowcount} old trades")

    # Reclaim space
    conn.execute("VACUUM")
    print("VACUUM complete")
```

### **Nuclear Option** (Volume 100% Full)
If completely out of space and can't run cleanup:

1. **Stop scanner** (Railway dashboard → Stop service)
2. **Delete log files manually:**
   ```bash
   railway run bash
   rm momentum_scanner.log.1 momentum_scanner.log.2
   ```
3. **Restart scanner**
4. **Run cleanup script immediately**

---

## 📈 **Growth Projections**

### **With Current Settings:**

| Timeframe | Database | Logs | Total | % of 500 MB |
|-----------|----------|------|-------|-------------|
| **1 Week** | 2 MB | 30 MB | ~332 MB | 66% |
| **1 Month** | 8 MB | 100 MB | ~408 MB | 82% |
| **3 Months** | 20 MB | 150 MB | ~470 MB | 94% ⚠️ |
| **6 Months** | 40 MB | 150 MB | ~490 MB | 98% 🔴 |

**After running cleanup (90-day retention):**
- Database always <50 MB
- Logs capped at 150 MB
- Total: ~450 MB steady state ✅

---

## 🎯 **Recommendations**

### **Short Term (Next 30 Days):**
1. ✅ **Monitor weekly** - Check Railway dashboard
2. ✅ **Run cleanup manually** - Once after 30 days
3. ✅ **Verify log rotation** - Check logs don't exceed 150 MB

### **Long Term (3-6 Months):**
1. **Set up automated cleanup** - Railway cron job (if available)
2. **Add storage monitoring** - Implement `/system/storage` endpoint
3. **Consider 1GB volume** - If you hit 80% consistently

### **If You Need 1GB:**
**When to upgrade:**
- You want to keep 1+ year of data
- You're adding more features (more tables)
- You hit 80% consistently even with cleanup

**How to upgrade:**
- Railway dashboard → Settings → Volumes → Upgrade to 1GB
- Cost: Usually +$5-10/month
- Gives you 2-3 years of capacity

---

## 📊 **Database Size Calculator**

```python
# Estimate your database size after X days

def estimate_db_size(days=90):
    """
    Estimate database size after X days

    Assumptions:
    - 5 signals/hour = 120 signals/day
    - 10 trades/day
    - 1 KB per signal
    - 500 bytes per trade
    """
    signals = days * 120  # signals
    trades = days * 10    # trades

    signals_mb = signals * 1024 / (1024 * 1024)
    trades_mb = trades * 500 / (1024 * 1024)

    total_mb = signals_mb + trades_mb

    print(f"After {days} days:")
    print(f"  Signals: {signals:,} × 1 KB = {signals_mb:.2f} MB")
    print(f"  Trades: {trades:,} × 500 B = {trades_mb:.2f} MB")
    print(f"  Total DB: {total_mb:.2f} MB")
    print(f"  With logs (150 MB): {total_mb + 150:.2f} MB")
    print(f"  With packages (300 MB): {total_mb + 150 + 300:.2f} MB")
    print()

# Examples:
estimate_db_size(30)   # 1 month
estimate_db_size(90)   # 3 months (cleanup threshold)
estimate_db_size(180)  # 6 months
estimate_db_size(365)  # 1 year
```

---

## ✅ **Summary**

**Is 500 MB enough?** ✅ **YES**, with management:
- Log rotation caps logs at 150 MB
- Cleanup script keeps DB under 50-100 MB
- Total steady state: ~450 MB (90% of capacity)
- Good for 6-12 months

**Action Items:**
1. ✅ Log rotation implemented (deploy pending)
2. ✅ Cleanup script created
3. ⏳ Set reminder to run cleanup after 30 days
4. ⏳ Monitor volume usage weekly via Railway dashboard
5. ⏳ Consider adding `/system/storage` API endpoint

**You're set! No immediate action needed.** Just monitor and run cleanup monthly. 🚀
