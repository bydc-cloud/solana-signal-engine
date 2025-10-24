# Helix Trading System

A Python-based automated trading system for cryptocurrency analysis and signal generation.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- API keys for Birdeye and Helius
- Telegram bot token and chat ID

### Installation
1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your API keys:
   ```
   BIRDEYE_API_KEY=your_birdeye_api_key
   HELIUS_API_KEY=your_helius_api_key
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   TELEGRAM_CHAT_ID=your_telegram_chat_id
   ```

### Running the System

#### Option 1: Interactive Mode
```bash
./START_MONEY_PRINTER.sh
```

#### Option 2: Autonomous Mode (Background)
```bash
./RUN_AUTONOMOUS.sh
```

#### Stop the System
```bash
./STOP_SCANNER.sh
```

## 📁 Key Components

- **REALITY_MOMENTUM_SCANNER.py** - Main momentum scanner
- **FINAL_NUCLEAR_HELIX_ENGINE.py** - Core trading engine
- **PRODUCTION_TELEGRAM_TRADER.py** - Telegram integration
- **NUCLEAR_HELIX_SOCIAL_ENGINE.py** - Social signal analysis

## 🔧 Configuration

The system scans tokens every 5 minutes and sends signals with:
- Signal strength threshold: 75+
- Market cap analysis
- Volume validation
- Risk assessment

## 📱 Features

- Real-time token scanning
- Telegram notifications
- Jupiter swap link generation
- Anti-duplicate protection
- Comprehensive logging

## 🎓 Graduation Trading System

An advanced Pump.fun graduation module now ships under `graduation/` with:
- Dual PAPER/LIVE modes with feature flags
- Gate and scoring pipeline (GS ≥ 72) before alerts
- Kelly-based sizing with strict exposure caps and safety rails
- Telegram graduation cards with deeplinks and admin controls

Enable it by extending `.env` with the following defaults:

```
GRAD_ENABLED=true
GRAD_MODE=PAPER
GRAD_PAPER_START_USD=100000
GRAD_PER_TRADE_CAP=0.005
GRAD_GLOBAL_EXPOSURE_CAP=0.50
GRAD_MAX_CONCURRENT=5
GRAD_DAILY_LOSS_CAP_PCT=-0.02
GRAD_KELLY_FRACTION=0.20
GRAD_SLIPPAGE_BPS_DEFAULT=200
GRAD_JITO_ENABLED=true
GRAD_JITO_TIP_PCTL=0.75
GRAD_LOCKER_REP_MIN=0.5
GRAD_SNIPER_PCT_MAX=0.35
GRAD_TOP10_PCT_MAX=0.60
GRAD_LP_LOCK_MIN_DAYS=30
```

Hook into your event loop:

```python
from graduation.detectors import on_lp_event, poll_pumpfun
from graduation.service import handle_candidate
from graduation.config import grad_cfg

if grad_cfg.enabled:
    helius.on('lp_create', lambda ev: asyncio.create_task(on_lp_event(ev)))
    scheduler.every(15).seconds.do(lambda: asyncio.create_task(poll_pumpfun()))
```

See `graduation/README.md` for deep-dive docs, migrations, and admin command details.

## ⚠️ Disclaimer

This software is for educational purposes only. Trading cryptocurrency involves substantial risk of loss. Use at your own risk.
# Updated: Fri Oct 24 16:19:39 PDT 2025
