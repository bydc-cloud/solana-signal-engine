# 🚀 Helix Trading System - Quick Start

## Current Status ✅

**Scanner:** Fixed and optimized (Oct 4, 2025)
**Graduation System:** Ready for paper trading
**Signal Generation:** Threshold gap resolved

---

## Run the Scanner

### Foreground (See Output)
```bash
cd /Users/johncox/Projects/helix/helix_production
python3 REALITY_MOMENTUM_SCANNER.py
```

### Background (Production)
```bash
./RUN_AUTONOMOUS.sh
```

### Stop Scanner
```bash
./STOP_SCANNER.sh
```

---

## Monitor Activity

### Watch Logs Live
```bash
tail -f momentum_scanner.log
```

### Check Recent Signals
```bash
tail -100 momentum_scanner.log | grep "MOMENTUM SIGNAL"
```

### View Scanner Stats
```bash
tail -100 momentum_scanner.log | grep "Scan complete"
```

---

## What Changed Today

### 1. Fixed Signal Generation 🎯
- **Problem**: Momentum threshold mismatch (28 vs 35)
- **Fix**: Aligned validation (20) and send (25) thresholds
- **Result**: Signals should now generate

### 2. Removed Pump.fun ❌
- **Problem**: Cloudflare 530 errors
- **Fix**: Using Helius events instead
- **Result**: No more scraping failures

### 3. Increased Discovery 📊
- **Before**: 4 strategies, 200 tokens max
- **Now**: 6 strategies, 300 tokens max
- **Result**: More opportunities per scan

---

## Expected Performance

**Per Scan Cycle (5 minutes):**
- Find: 250-300 tokens
- Filter: 15-25 candidates
- Signal: 3-10 high-quality opportunities

**Per Day:**
- Scans: 288 (every 5 min)
- Signals: 15-50 depending on market

---

## Graduation System Setup

### Enable Paper Trading
Edit `.env`:
```bash
GRAD_ENABLED=true
GRAD_MODE=PAPER
GRAD_PAPER_START_USD=100000
```

### Monitor Paper Trades
```bash
# View graduation alerts
tail -f momentum_scanner.log | grep "Graduation"

# Check paper equity
sqlite3 data/graduation.db "SELECT * FROM grad_paper_equity ORDER BY ts DESC LIMIT 10"
```

### Admin Commands (Telegram)
- `/mode PAPER|LIVE` - Switch modes
- `/positions` - View open positions
- `/risk` - Check risk metrics
- `/pause` / `/resume` - Control trading

---

## Troubleshooting

### No Signals Generating
```bash
# Check if scanner is running
ps aux | grep REALITY_MOMENTUM_SCANNER

# Check recent errors
tail -50 momentum_scanner.log | grep ERROR

# Verify API keys
grep -E "BIRDEYE|HELIUS|TELEGRAM" .env
```

### API Rate Limits
```bash
# Reduce scan frequency in code:
# Change: self.min_scan_interval = 300  (5 min)
# To:     self.min_scan_interval = 600  (10 min)
```

### High Memory Usage
```bash
# Clear cache manually
rm -f data/scanner_metrics.json
```

---

## Files Overview

### Main Components
- `REALITY_MOMENTUM_SCANNER.py` - Main scanner
- `graduation/` - Trading system module
- `.env` - API keys and config
- `momentum_scanner.log` - All activity logs

### Configuration
- Signal threshold: 25
- Momentum minimum: 25
- Market cap: $10k-$50k
- Scan interval: 5 minutes

### Data Files
- `data/scanner_metrics.json` - Performance stats
- `data/graduation.db` - Trade journal
- `data/*.json` - Token cache

---

## Next Steps

1. **Run Scanner** - Test for 30-60 minutes
2. **Monitor Signals** - Verify quality
3. **Enable Graduation** - Set `GRAD_ENABLED=true`
4. **Paper Trade** - Watch for 3-7 days
5. **Go Live** - Switch to `GRAD_MODE=LIVE` with low caps

---

## Support

**Logs:** `momentum_scanner.log`
**Config:** `.env`
**Docs:** `README.md`, `graduation/README.md`
**Summary:** `SIGNAL_FIX_SUMMARY.md`
