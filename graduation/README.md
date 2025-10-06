# Graduation Trading System

The Graduation system extends the existing bot with a dedicated pipeline for spotting Pump.fun launches that are about to graduate or have just graduated to a live liquidity pool.

## Features
- Dual mode operation (PAPER/LIVE) with runtime toggles
- Pump.fun + Helius detectors feeding a modular service layer
- Hard gates covering sellability, authority revocation, LP lockers, holder quality, and creator history
- Weighted graduation score (GS) with Telegram card notifications
- Multi-class model (loser/winner/mega) with Kelly sizing and exposure caps
- Live execution wrapper (Jupiter + Jito tip support) and simulated paper engine
- Append-only journaling with migrations for alerts, trades, exposure, and blocklists
- Admin controls: `/mode`, `/pause`, `/resume`, `/sizecap`, `/exposure`, `/positions`, `/risk`, `/kill`

## Getting Started
1. Ensure the new environment variables are present in `.env` (defaults favour PAPER mode):
   ```env
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
2. Wire the detectors and service into the main event loop:
   ```python
   from graduation.detectors import on_lp_event, poll_pumpfun
   from graduation.service import handle_candidate
   from graduation.config import grad_cfg

   if grad_cfg.enabled:
       helius.on('lp_create', lambda ev: asyncio.create_task(on_lp_event(ev)))
       scheduler.every(15).seconds.do(lambda: asyncio.create_task(poll_pumpfun()))
   ```
3. Run the database migration once (automatically triggered on service import) or explicitly via:
   ```bash
   python -m graduation.migrate
   ```
4. Execute tests with `python -m unittest tests/test_graduation_pipeline.py`.

## Admin Controls
Commands must originate from approved admins (`GRAD_ADMIN_IDS` comma list). Responses are plain text for Telegram bots.

- `/mode PAPER|LIVE`
- `/pause`, `/resume`
- `/sizecap 0.0025`, `/exposure 0.25`
- `/positions`, `/risk`
- `/kill` switches to alerts-only for two hours

## Paper-to-Live Checklist
1. Observe PAPER telemetry for 3–7 days (monitor `grad_paper_equity` table & Telegram cards)
2. If satisfied, flip `GRAD_MODE=LIVE` and lower caps (`GRAD_PER_TRADE_CAP=0.001`, `GRAD_GLOBAL_EXPOSURE_CAP=0.10`)
3. Increase caps gradually when exposure tracking remains stable
4. Keep daily loss guardrails engaged; the system auto-falls back to PAPER when breached
