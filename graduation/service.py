
"""Graduation service orchestrates detection to execution."""

from __future__ import annotations

import logging
from typing import Any

from .config import grad_cfg, grad_state
from .enrich import enrich_candidate
from .gates import evaluate_gates
from .journal import apply_migrations, journal_alert, journal_paper_equity, journal_trade
from .model import grad_model
from .notify import send_graduation_alert
from .paper import execute_paper_trade
from .sizing import compute_sizing
from .types import ExecutionReport, GraduationCandidateSeed, ModelOutput, SizingDecision
from .scoring import compute_graduation_score
from .exec import execute_live_trade

logger = logging.getLogger(__name__)

apply_migrations()


def _is_test_token(seed: GraduationCandidateSeed) -> bool:
    """Filter out test, fake, or invalid tokens."""
    # Check for test/fake keywords in symbol
    symbol_upper = seed.symbol.upper()
    test_keywords = ['TEST', 'FAKE', 'DEMO', 'SAMPLE', 'EXAMPLE', 'DEBUG', 'DEV']
    if any(keyword in symbol_upper for keyword in test_keywords):
        return True

    # Check for test/fake keywords in address
    address_upper = seed.address.upper()
    if any(keyword in address_upper for keyword in test_keywords):
        return True

    # Validate Solana address format (base58, 32-44 chars typically)
    if len(seed.address) < 32 or len(seed.address) > 44:
        return True

    # Check for obviously fake addresses (repeated chars, sequential patterns)
    if seed.address == seed.address[0] * len(seed.address):  # All same character
        return True

    return False


def _to_seed(payload: Any) -> GraduationCandidateSeed:
    if isinstance(payload, GraduationCandidateSeed):
        return payload
    if isinstance(payload, dict):
        address = payload.get("address") or payload.get("mint") or payload.get("token_address")
        if not address:
            raise ValueError("Candidate payload missing address")
        symbol = payload.get("symbol") or payload.get("name") or address[:6].upper()
        curve = payload.get("curve_pct") or payload.get("curvePct")
        return GraduationCandidateSeed(address=address, symbol=symbol, pumpfun_curve_pct=curve, raw=payload, source=payload.get("source", "unknown"))
    raise TypeError(f"Unsupported candidate payload: {type(payload)}")


async def handle_candidate(payload: Any) -> None:
    if not grad_cfg.enabled:
        return

    try:
        seed = _to_seed(payload)
    except Exception as exc:
        logger.error("Failed to normalize candidate payload: %s", exc)
        return

    # Filter out test/fake tokens
    if _is_test_token(seed):
        logger.debug("Skipping test/fake token: %s (%s)", seed.symbol, seed.address)
        return

    try:
        enriched = await enrich_candidate(seed)
    except Exception as exc:
        logger.exception("Enrichment failed for %s: %s", seed.address, exc)
        return

    gate_result = evaluate_gates(enriched)
    scoring = compute_graduation_score(enriched)

    # Lower threshold for learning mode - get GRAD_MIN_SCORE from env or default to 35
    import os
    min_score = float(os.getenv('GRAD_MIN_SCORE', '35'))

    if not gate_result.passed or scoring.gs < min_score:
        probs = ModelOutput(1.0, 0.0, 0.0)
        rationale = "gate_blocked" if not gate_result.passed else "score_below_threshold"
        decision = SizingDecision(size_fraction=0.0, ev=0.0, variance=1.0, kelly_fraction=0.0, mode=grad_cfg.mode, rationale=rationale)
        journal_alert(enriched, scoring, probs, decision, gate_result)
        logger.info("Graduation candidate %s filtered (gate=%s gs=%.2f min=%.2f)", enriched.address, gate_result.passed, scoring.gs, min_score)
        return

    snapshot = await grad_state.snapshot()
    probs = grad_model.predict(enriched, scoring)
    decision = await compute_sizing(probs, open_exposure=snapshot.get("open_exposure", 0.0), open_positions=int(snapshot.get("concurrent", 0)))
    journal_alert(enriched, scoring, probs, decision, gate_result)

    if not decision.should_trade():
        logger.info("Graduation candidate %s produced no trade (reason=%s)", enriched.address, decision.rationale)
        return

    if decision.mode == "LIVE":
        report = await execute_live_trade(enriched, decision)
        if not report.success:
            logger.warning("Graduation LIVE execution failed for %s: %s", enriched.address, report.error)
            return
        await grad_state.add_position(enriched.address, decision.size_fraction, snapshot.get("paper_equity", grad_cfg.paper_start_usd) * decision.size_fraction)
    else:
        report = await execute_paper_trade(enriched, decision)
        if not report.success:
            logger.warning("Graduation paper execution failed for %s: %s", enriched.address, report.error)
            return

    journal_trade(enriched, decision, report)
    await send_graduation_alert(enriched, scoring, probs, decision, gate_result)

    refreshed = await grad_state.snapshot()
    journal_paper_equity(refreshed)

    logger.info("Graduation pipeline completed for %s (mode=%s size=%.4f)", enriched.address, decision.mode, decision.size_fraction)
