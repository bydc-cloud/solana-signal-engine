"""Graduation scoring model."""

from __future__ import annotations

import math
from typing import Dict

from .types import EnrichedCandidate, ScoringResult


def compute_graduation_score(candidate: EnrichedCandidate) -> ScoringResult:
    subscores = {
        "LP_score": _lp_score(candidate),
        "Momentum_score": _momentum_score(candidate),
        "Holder_quality": _holder_quality(candidate),
        "Whale_inflow": _whale_inflow(candidate),
        "Smart_money": _smart_money_score(candidate),  # NEW: Nansen smart money
        "Creator_provenance": _creator_provenance(candidate),
        "Liquidity_migration": _liquidity_migration(candidate),
        "Contract_sanity": _contract_sanity(candidate),
        "Sellability_sim": 100.0 if candidate.risk.get("sellability_sim_ok") else 0.0,
    }

    weights = {
        "LP_score": 0.18,  # Reduced slightly
        "Momentum_score": 0.14,  # Reduced slightly
        "Holder_quality": 0.12,
        "Whale_inflow": 0.10,
        "Smart_money": 0.12,  # NEW: Smart money gets 12% weight
        "Creator_provenance": 0.10,
        "Liquidity_migration": 0.09,
        "Contract_sanity": 0.09,
        "Sellability_sim": 0.06,
    }

    gs = sum(subscores[name] * weight for name, weight in weights.items())
    candidate.scoring_inputs = subscores
    return ScoringResult(gs=round(gs, 2), subscores=subscores)


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _sigmoid(value: float, midpoint: float, spread: float) -> float:
    if spread == 0:
        return 0.0
    return 1 / (1 + math.exp(-(value - midpoint) / spread))


def _lp_score(candidate: EnrichedCandidate) -> float:
    risk = candidate.risk
    market = candidate.market

    locker_rep = float(risk.get("locker_rep_score", 0.0) or 0.0)
    locker_component = _clamp(locker_rep * 100, 0, 100)

    lock_days = float(risk.get("lock_days", 0.0) or 0.0)
    lock_component = _sigmoid(lock_days, midpoint=45, spread=8) * 100

    lp_locked_pct = float(risk.get("lp_locked_pct", market.get("lp_locked_pct", 0.0) or 0.0))
    lp_locked_component = _clamp(lp_locked_pct, 0, 90) / 90 * 100

    supply_in_lp_pct = float(market.get("supply_in_lp_pct", 0.0) or 0.0)
    if supply_in_lp_pct <= 25:
        supply_component = (supply_in_lp_pct / 25) * 100
    elif supply_in_lp_pct >= 75:
        supply_component = (100 - supply_in_lp_pct) / 25 * 100
    else:
        supply_component = 100
    supply_component = _clamp(supply_component, 0, 100)

    score = (
        0.40 * locker_component
        + 0.30 * lock_component
        + 0.20 * lp_locked_component
        + 0.10 * supply_component
    )
    return _clamp(score, 0, 100)


def _momentum_score(candidate: EnrichedCandidate) -> float:
    market = candidate.market
    analytics = candidate.analytics

    vol_15m = float(market.get("vol_15m_usd", 0.0) or 0.0)
    z_score = _clamp(vol_15m / 5_000, 0, 4)
    z_component = (z_score / 4) * 60

    buy_volume = analytics.get("buy_volume", 0.0)
    sell_volume = analytics.get("sell_volume", 0.0)
    total_volume = buy_volume + sell_volume
    buy_ratio = buy_volume / total_volume if total_volume else 0.0
    buy_component = _clamp(buy_ratio * 100, 0, 100) * 0.4

    return _clamp(z_component + buy_component, 0, 100)


def _holder_quality(candidate: EnrichedCandidate) -> float:
    risk = candidate.risk

    smart_wallet_bonus = float(risk.get("smart_wallet_pct", 0.0) or 0.0) * 0.5
    holder_velocity = float(risk.get("holder_velocity", 0.0) or 0.0)
    velocity_component = _clamp(holder_velocity * 10, 0, 40)
    top10_penalty = _clamp(float(risk.get("top10_pct", 0.0) or 0.0) * 100, 0, 100) * 0.4
    sniper_penalty = _clamp(float(risk.get("sniper_pct", 0.0) or 0.0) * 100, 0, 100) * 0.3
    insider_penalty = _clamp(float(risk.get("insider_pct", 0.0) or 0.0) * 100, 0, 100) * 0.3

    raw_score = 60 + smart_wallet_bonus + velocity_component - top10_penalty - sniper_penalty - insider_penalty
    return _clamp(raw_score, 0, 100)


def _whale_inflow(candidate: EnrichedCandidate) -> float:
    inflow = float(candidate.analytics.get("whales_inflow", 0.0) or 0.0)
    market_cap = float(candidate.market.get("market_cap", 0.0) or 0.0)
    if market_cap <= 0:
        return 0.0
    ratio = _clamp(inflow / max(10_000, market_cap) * 100, 0, 100)
    return ratio


def _creator_provenance(candidate: EnrichedCandidate) -> float:
    risk = candidate.risk
    success = int(risk.get("creator_success_10x", 0) or 0)
    rugs = int(risk.get("creator_flagged_rugs", 0) or 0)
    cluster_flag = 20 if risk.get("creator_blocklisted") else 0

    base = 70 + success * 5 - rugs * 25 - cluster_flag
    return _clamp(base, 0, 100)


def _liquidity_migration(candidate: EnrichedCandidate) -> float:
    analytics = candidate.analytics
    adds = analytics.get("lp_adds", 0)
    removes = analytics.get("lp_removes", 0)
    dev_delta = analytics.get("dev_liquidity_delta", 0.0)
    volatility = analytics.get("volatility_15m", 0.0)

    base = 50 + adds * 5 - removes * 15 + dev_delta * 10 - volatility * 10
    return _clamp(base, 0, 100)


def _contract_sanity(candidate: EnrichedCandidate) -> float:
    risk = candidate.risk
    taxes = float(risk.get("tax_pct", 0.0) or 0.0)
    blacklist = bool(risk.get("has_blacklist", False))
    whitelist = bool(risk.get("has_whitelist", False))
    authorities_ok = risk.get("mint_revoked", False) and risk.get("freeze_revoked", False)

    base = 100 - taxes * 30
    if blacklist:
        base -= 40
    if whitelist:
        base -= 40
    if not authorities_ok:
        base -= 30
    return _clamp(base, 0, 100)
