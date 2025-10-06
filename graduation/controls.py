"""Admin command handlers for the Graduation system."""

from __future__ import annotations

import asyncio
import os
from typing import Optional

from .config import grad_cfg, grad_state

ADMIN_IDS = {item.strip() for item in os.getenv("GRAD_ADMIN_IDS", "").split(",") if item.strip()}


def _is_authorized(user_id: Optional[str]) -> bool:
    if not ADMIN_IDS:
        return True
    return str(user_id) in ADMIN_IDS


async def handle_command(command: str, args: str, user_id: Optional[str] = None) -> str:
    if not _is_authorized(user_id):
        return "🚫 Unauthorized"

    cmd = command.lower()
    if cmd == "/pause":
        await grad_state.set_paused(True)
        return "⏸️ Graduation system paused"
    if cmd == "/resume":
        await grad_state.set_paused(False)
        return "▶️ Graduation system resumed"
    if cmd == "/mode":
        mode = args.strip().upper() or ("LIVE" if grad_cfg.is_live() else "PAPER")
        await grad_state.record_mode(mode)
        return f"🔁 Graduation mode set to {mode}"
    if cmd == "/sizecap":
        try:
            value = float(args.strip())
        except ValueError:
            return "⚠️ Usage: /sizecap <fraction>"
        grad_cfg.per_trade_cap = value
        return f"📐 Per-trade cap updated to {value:.4f}"
    if cmd == "/exposure":
        try:
            value = float(args.strip())
        except ValueError:
            return "⚠️ Usage: /exposure <fraction>"
        grad_cfg.global_exposure_cap = value
        return f"📊 Global exposure cap updated to {value:.2f}"
    if cmd == "/positions":
        snap = await grad_state.snapshot()
        return f"📈 Open exposure {snap['open_exposure']*100:.2f}% across {snap['concurrent']} positions"
    if cmd == "/risk":
        snap = await grad_state.snapshot()
        return (
            "🛡️ Risk status
"
            f"Mode: {grad_cfg.mode}
"
            f"Paused: {snap['paused']}
"
            f"Daily PnL: {snap['daily_realized_pct']*100:.2f}%
"
            f"Kill switch until: {snap['kill_switch_until']}"
        )
    if cmd == "/kill":
        await grad_state.set_kill_switch(120)
        await grad_state.set_paused(True)
        return "🛑 Kill switch engaged for 2h"
    if cmd == "/help":
        return "Commands: /mode /pause /resume /sizecap /exposure /positions /risk /kill"

    return "❓ Unknown command"
