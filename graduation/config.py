"""Configuration and runtime state for the Graduation trading system."""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional


def _get_env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _get_env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _get_env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


@dataclass
class GraduationConfig:
    enabled: bool
    mode: str
    paper_start_usd: float
    per_trade_cap: float
    global_exposure_cap: float
    max_concurrent: int
    daily_loss_cap_pct: float
    kelly_fraction: float
    slippage_bps_default: int
    jito_enabled: bool
    jito_tip_pct: float
    locker_rep_min: float
    sniper_pct_max: float
    top10_pct_max: float
    lp_lock_min_days: int

    @classmethod
    def from_env(cls) -> "GraduationConfig":
        return cls(
            enabled=_get_env_bool("GRAD_ENABLED", True),
            mode=os.getenv("GRAD_MODE", "PAPER").upper(),
            paper_start_usd=_get_env_float("GRAD_PAPER_START_USD", 100_000.0),
            per_trade_cap=_get_env_float("GRAD_PER_TRADE_CAP", 0.005),
            global_exposure_cap=_get_env_float("GRAD_GLOBAL_EXPOSURE_CAP", 0.50),
            max_concurrent=_get_env_int("GRAD_MAX_CONCURRENT", 5),
            daily_loss_cap_pct=_get_env_float("GRAD_DAILY_LOSS_CAP_PCT", -0.02),
            kelly_fraction=_get_env_float("GRAD_KELLY_FRACTION", 0.20),
            slippage_bps_default=int(_get_env_float("GRAD_SLIPPAGE_BPS_DEFAULT", 200)),
            jito_enabled=_get_env_bool("GRAD_JITO_ENABLED", True),
            jito_tip_pct=_get_env_float("GRAD_JITO_TIP_PCTL", 0.75),
            locker_rep_min=_get_env_float("GRAD_LOCKER_REP_MIN", 0.5),
            sniper_pct_max=_get_env_float("GRAD_SNIPER_PCT_MAX", 0.35),
            top10_pct_max=_get_env_float("GRAD_TOP10_PCT_MAX", 0.60),
            lp_lock_min_days=_get_env_int("GRAD_LP_LOCK_MIN_DAYS", 30),
        )

    def is_live(self) -> bool:
        return self.mode == "LIVE"

    def is_paper(self) -> bool:
        return self.mode == "PAPER"


class GraduationState:
    """Tracks runtime exposure, kill switches, and paper equity."""

    def __init__(self, cfg: GraduationConfig) -> None:
        self.cfg = cfg
        self._lock = asyncio.Lock()
        self.reset_daily_metrics()
        self.paper_equity_usd = cfg.paper_start_usd
        self.paper_realized_pnl_usd = 0.0
        self.paper_unrealized_pnl_usd = 0.0
        self.positions: Dict[str, Dict[str, float]] = {}
        self.kill_switch_until: Optional[datetime] = None
        self.paused = False
        self.consecutive_losers = []  # timestamps of losers

    def reset_daily_metrics(self) -> None:
        self.daily_anchor = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        self.daily_realized_pnl_pct = 0.0
        self.daily_loss_mode_triggered = False

    async def snapshot(self) -> Dict[str, float]:
        async with self._lock:
            self._roll_daily_reset()
            exposure = sum(p["fraction"] for p in self.positions.values())
            return {
                "open_exposure": exposure,
                "concurrent": len(self.positions),
                "paper_equity": self.paper_equity_usd,
                "paper_realized": self.paper_realized_pnl_usd,
                "paper_unrealized": self.paper_unrealized_pnl_usd,
                "daily_realized_pct": self.daily_realized_pnl_pct,
                "kill_switch_until": self.kill_switch_until.isoformat() if self.kill_switch_until else None,
                "paused": self.paused,
            }

    async def can_enter(self, size_fraction: float) -> (bool, Optional[str]):
        async with self._lock:
            self._roll_daily_reset()
            if self.paused:
                return False, "paused"
            now = datetime.now(timezone.utc)
            if self.kill_switch_until and now < self.kill_switch_until:
                return False, "kill_switch_active"
            exposure = sum(p["fraction"] for p in self.positions.values())
            if exposure + size_fraction > self.cfg.global_exposure_cap + 1e-9:
                return False, "global_exposure_cap"
            if len(self.positions) >= self.cfg.max_concurrent:
                return False, "max_concurrent"
            if self.daily_loss_mode_triggered:
                return False, "daily_loss_cap"
            return True, None

    async def add_position(self, address: str, size_fraction: float, notional_usd: float) -> None:
        async with self._lock:
            self._roll_daily_reset()
            self.positions[address] = {"fraction": size_fraction, "notional_usd": notional_usd, "opened_at": datetime.now(timezone.utc).isoformat()}

    async def close_position(self, address: str, realized_pnl_pct: float) -> None:
        async with self._lock:
            self._roll_daily_reset()
            position = self.positions.pop(address, None)
            if position:
                self.daily_realized_pnl_pct += realized_pnl_pct
                if realized_pnl_pct < 0:
                    self.consecutive_losers.append(datetime.now(timezone.utc))
                    self._enforce_kill_switch()
                else:
                    self.consecutive_losers.clear()
                if self.daily_realized_pnl_pct <= self.cfg.daily_loss_cap_pct:
                    self.daily_loss_mode_triggered = True
                    self.cfg.mode = "PAPER"

    async def record_paper_fill(self, pnl_usd: float, unrealized_usd: float) -> None:
        async with self._lock:
            self.paper_realized_pnl_usd += pnl_usd
            self.paper_unrealized_pnl_usd = unrealized_usd
            self.paper_equity_usd = self.cfg.paper_start_usd + self.paper_realized_pnl_usd + self.paper_unrealized_pnl_usd

    async def set_paused(self, value: bool) -> None:
        async with self._lock:
            self.paused = value

    async def set_kill_switch(self, minutes: int) -> None:
        async with self._lock:
            self.kill_switch_until = datetime.now(timezone.utc) + timedelta(minutes=minutes)

    async def record_mode(self, mode: str) -> None:
        async with self._lock:
            self.cfg.mode = mode.upper()

    def _roll_daily_reset(self) -> None:
        now = datetime.now(timezone.utc)
        if now - self.daily_anchor >= timedelta(days=1):
            self.daily_anchor = now.replace(hour=0, minute=0, second=0, microsecond=0)
            self.daily_realized_pnl_pct = 0.0
            self.daily_loss_mode_triggered = False
            self.consecutive_losers.clear()

    def _enforce_kill_switch(self) -> None:
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=90)
        self.consecutive_losers = [ts for ts in self.consecutive_losers if ts >= cutoff]
        if len(self.consecutive_losers) >= 3:
            self.kill_switch_until = now + timedelta(hours=2)


grad_cfg = GraduationConfig.from_env()
grad_state = GraduationState(grad_cfg)
