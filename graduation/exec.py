"""Execution wrapper for Graduation LIVE trades."""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, Dict, Optional

from .config import grad_cfg
from .types import EnrichedCandidate, ExecutionReport, SizingDecision

logger = logging.getLogger(__name__)

DEFAULT_JITO_TIP_LAMPORTS = 2_000_000  # ~0.002 SOL fallback


def _estimate_slippage_bps(candidate: EnrichedCandidate) -> int:
    liquidity = float(candidate.market.get("liquidity", 0.0) or 0.0)
    vol_15m = float(candidate.market.get("vol_15m_usd", 0.0) or 0.0)
    dynamic = min(200, max(50, int(150 * (vol_15m / max(liquidity, 1)))))
    return max(50, min(200, dynamic))


def _build_oco_payload(candidate: EnrichedCandidate, entry_price: float) -> Dict[str, Any]:
    price_levels = [entry_price * 2.0, entry_price * 3.5, entry_price * 5.0]
    atr = candidate.analytics.get("atr_1m", 0.0) or entry_price * 0.1
    trailing = 1.2 * atr
    return {
        "tp_levels": price_levels,
        "trailing_stop": trailing,
        "token": candidate.address,
    }


async def execute_live_trade(candidate: EnrichedCandidate, decision: SizingDecision, executor: Optional[Any] = None) -> ExecutionReport:
    if not decision.should_trade():
        return ExecutionReport(success=False, error="no_trade")

    slippage_bps = _estimate_slippage_bps(candidate)
    jito_tip = DEFAULT_JITO_TIP_LAMPORTS if grad_cfg.jito_enabled else 0

    if executor and hasattr(executor, "swap"):
        try:
            route = await executor.swap(
                mint=candidate.address,
                size_fraction=decision.size_fraction,
                max_slippage_bps=slippage_bps,
                jito_tip_lamports=jito_tip,
            )
            return ExecutionReport(success=True, txid=route.get("txid"), route=route.get("route"), slippage_bps=slippage_bps, jito_tip_lamports=jito_tip, oco_payload=_build_oco_payload(candidate, route.get("entry_price", 0.0)))
        except Exception as exc:
            logger.exception("Executor swap failed: %s", exc)
            return ExecutionReport(success=False, error=str(exc))

    logger.info("No executor provided. Simulating live trade for %s", candidate.address)
    await asyncio.sleep(0.5)
    entry_price = float(candidate.market.get("price", 0.0) or 0.0)
    return ExecutionReport(success=True, txid="SIMULATED", route="Jupiter", slippage_bps=slippage_bps, jito_tip_lamports=jito_tip, oco_payload=_build_oco_payload(candidate, entry_price))
