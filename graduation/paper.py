"""Paper trading simulator for Graduation."""

from __future__ import annotations

import asyncio
import random
from typing import Dict

from .config import grad_state
from .exec import _build_oco_payload
from .types import EnrichedCandidate, ExecutionReport, SizingDecision


async def execute_paper_trade(candidate: EnrichedCandidate, decision: SizingDecision) -> ExecutionReport:
    if not decision.should_trade():
        return ExecutionReport(success=False, error="no_trade")

    snapshot = await grad_state.snapshot()
    equity = snapshot.get("paper_equity", 100_000.0)
    notional = equity * decision.size_fraction

    latency = random.uniform(2.0, 5.0)
    await asyncio.sleep(latency)

    slippage_bps = random.randint(150, 350)
    entry_price = float(candidate.market.get("price", 0.0) or 0.0)
    slip_price = entry_price * (1 + slippage_bps / 10_000)

    await grad_state.add_position(candidate.address, decision.size_fraction, notional)
    await grad_state.record_paper_fill(pnl_usd=0.0, unrealized_usd=0.0)

    return ExecutionReport(
        success=True,
        txid="PAPER",
        route="paper",
        slippage_bps=slippage_bps,
        oco_payload=_build_oco_payload(candidate, slip_price),
    )
