"""Position sizing for Graduation trades."""

from __future__ import annotations

from typing import Optional

from .config import grad_cfg, grad_state
from .types import ModelOutput, SizingDecision

LOSER_PAYOFF = -0.70
WINNER_PAYOFF = 10.0
MEGA_PAYOFF = 50.0


async def compute_sizing(probs: ModelOutput, open_exposure: float, open_positions: int) -> SizingDecision:
    ev = probs.p0 * LOSER_PAYOFF + probs.p1 * WINNER_PAYOFF + probs.p2 * MEGA_PAYOFF
    e2 = probs.p0 * LOSER_PAYOFF ** 2 + probs.p1 * WINNER_PAYOFF ** 2 + probs.p2 * MEGA_PAYOFF ** 2
    variance = max(1e-9, e2 - ev ** 2)

    if ev <= 0:
        return SizingDecision(size_fraction=0.0, ev=ev, variance=variance, kelly_fraction=0.0, mode=grad_cfg.mode, rationale="non_positive_ev")

    f_kelly = max(0.0, ev / variance)
    f_target = min(grad_cfg.kelly_fraction * f_kelly, grad_cfg.per_trade_cap)
    available = max(0.0, grad_cfg.global_exposure_cap - open_exposure)
    size_fraction = min(f_target, available)
    capped_by: Optional[str] = None

    if size_fraction < f_target - 1e-6:
        capped_by = "exposure_cap"

    allowed, reason = True, None
    if size_fraction > 0:
        allowed, reason = await grad_state.can_enter(size_fraction)

    if not allowed:
        return SizingDecision(size_fraction=0.0, ev=ev, variance=variance, kelly_fraction=f_kelly, mode=grad_cfg.mode, rationale=reason or "blocked")

    if open_positions >= grad_cfg.max_concurrent:
        return SizingDecision(size_fraction=0.0, ev=ev, variance=variance, kelly_fraction=f_kelly, mode=grad_cfg.mode, rationale="max_concurrent")

    return SizingDecision(size_fraction=size_fraction, ev=ev, variance=variance, kelly_fraction=f_kelly, mode=grad_cfg.mode, rationale="sized", capped_by=capped_by)
