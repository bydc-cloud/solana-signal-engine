"""Hard risk gates for Graduation candidates."""

from __future__ import annotations

import logging
from typing import Optional

from .config import grad_cfg
from .types import EnrichedCandidate, GateCheck, GateResult

logger = logging.getLogger(__name__)


def _check(name: str, condition: bool, reason: Optional[str] = None) -> GateCheck:
    return GateCheck(name=name, passed=bool(condition), reason=None if condition else reason or name)


def evaluate_gates(candidate: EnrichedCandidate) -> GateResult:
    risk = candidate.risk

    def _missing(field: str) -> Optional[str]:
        return f"missing_{field}" if risk.get(field) is None else None

    checks = [
        _check("sellability_sim", risk.get("sellability_sim_ok", False), risk.get("sellability_context") or "sellability_failed"),
        _check("mint_revoked", risk.get("mint_revoked", False), _missing("mint_revoked")),
        _check("freeze_revoked", risk.get("freeze_revoked", False), _missing("freeze_revoked")),
        _check(
            "lp_locked", 
            risk.get("lp_locked_bool", False) and float(risk.get("lock_days", 0)) >= grad_cfg.lp_lock_min_days,
            "lp_not_locked_enough",
        ),
        _check(
            "locker_reputation",
            float(risk.get("locker_rep_score", 0.0)) >= grad_cfg.locker_rep_min,
            "locker_rep_low",
        ),
        _check(
            "sniper_concentration",
            float(risk.get("sniper_pct", 1.0)) <= grad_cfg.sniper_pct_max,
            "sniper_pct_exceeds",
        ),
        _check(
            "top10_concentration",
            float(risk.get("top10_pct", 1.0)) <= grad_cfg.top10_pct_max,
            "top10_pct_exceeds",
        ),
        _check(
            "creator_blocklist",
            not bool(risk.get("creator_blocklisted", False)),
            "creator_blocklisted",
        ),
        _check(
            "creator_recent_rugs",
            int(risk.get("creator_flagged_rugs", 0) or 0) < 2,
            "creator_recent_rugs",
        ),
    ]

    passed = all(check.passed for check in checks)
    if not passed:
        failed = [c.name for c in checks if not c.passed]
        logger.info("Graduation gate rejected %s: %s", candidate.address, ",".join(failed))

    candidate.gates = {c.name: c.passed for c in checks}
    return GateResult(passed=passed, checks=checks)
