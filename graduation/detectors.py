"""Detectors transform external events into graduation candidates.

Uses Helius for LP creation events and Birdeye/Nansen for token enrichment.
No Pump.fun scraping required.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

import aiohttp

from .config import grad_cfg
from .types import GraduationCandidateSeed

logger = logging.getLogger(__name__)


def _extract_symbol(raw_symbol: Optional[str], address: str) -> str:
    if raw_symbol and raw_symbol.strip():
        return raw_symbol.strip()[:16]
    return address[:6].upper()


async def on_lp_event(event: Dict[str, Any]) -> None:
    """Handle Helius LP creation event and forward to the graduation pipeline."""
    if not grad_cfg.enabled:
        return

    mint = event.get("mint") or event.get("mintAddress") or event.get("token")
    if not mint:
        logger.debug("Ignoring LP event without mint: %s", event)
        return

    symbol = _extract_symbol(event.get("symbol"), mint)
    curve_pct = None
    metadata = event.get("metadata") or {}
    if isinstance(metadata, dict):
        curve_pct = metadata.get("curve_pct") or metadata.get("curvePercent")
        if isinstance(curve_pct, str):
            try:
                curve_pct = float(curve_pct)
            except ValueError:
                curve_pct = None

    seed = GraduationCandidateSeed(
        address=mint,
        symbol=symbol,
        pumpfun_curve_pct=curve_pct,
        source="helius_lp",
        lp_event=event,
        raw=event,
    )

    logger.info("Graduation LP event detected for %s (%s)", symbol, mint)

    from .service import handle_candidate  # Local import to avoid circular dependency

    await handle_candidate(seed)


async def detect_new_liquidity_pools(session: Optional[aiohttp.ClientSession] = None) -> None:
    """
    Monitor Helius for new LP creation events on Solana.
    This replaces Pump.fun polling with real-time blockchain data.
    """
    if not grad_cfg.enabled:
        return

    # Note: This would typically be called by a Helius webhook or WebSocket subscription
    # For now, the on_lp_event function handles individual LP events
    # Future enhancement: Add Helius transaction monitoring for LP creation
    logger.debug("LP monitoring active via Helius events")


async def bootstrap_detectors() -> None:
    """Eagerly warm up detectors if the mode is enabled."""
    if not grad_cfg.enabled:
        return
    logger.info("Graduation detectors bootstrapped at %s", datetime.now(timezone.utc).isoformat())
