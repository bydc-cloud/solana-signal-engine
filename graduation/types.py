"""Shared data structures for the Graduation system."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class GraduationCandidateSeed:
    address: str
    symbol: str
    detected_at: datetime = field(default_factory=utc_now)
    source: str = "unknown"
    pumpfun_curve_pct: Optional[float] = None
    lp_event: Optional[Dict[str, Any]] = None
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnrichedCandidate:
    seed: GraduationCandidateSeed
    market: Dict[str, Any]
    onchain: Dict[str, Any]
    risk: Dict[str, Any]
    analytics: Dict[str, Any]
    gates: Dict[str, Any] = field(default_factory=dict)
    scoring_inputs: Dict[str, Any] = field(default_factory=dict)

    @property
    def address(self) -> str:
        return self.seed.address

    @property
    def symbol(self) -> str:
        return self.seed.symbol


@dataclass
class GateCheck:
    name: str
    passed: bool
    reason: Optional[str] = None


@dataclass
class GateResult:
    passed: bool
    checks: Sequence[GateCheck]

    def reasons(self) -> List[str]:
        return [c.reason for c in self.checks if c.reason]


@dataclass
class ScoringResult:
    gs: float
    subscores: Dict[str, float]


@dataclass
class ModelOutput:
    p0: float
    p1: float
    p2: float

    def as_dict(self) -> Dict[str, float]:
        return {"loser": self.p0, "winner": self.p1, "mega": self.p2}


@dataclass
class SizingDecision:
    size_fraction: float
    ev: float
    variance: float
    kelly_fraction: float
    mode: str
    rationale: str
    capped_by: Optional[str] = None

    def should_trade(self) -> bool:
        return self.size_fraction > 0 and self.ev > 0


@dataclass
class ExecutionReport:
    success: bool
    txid: Optional[str] = None
    route: Optional[str] = None
    slippage_bps: Optional[int] = None
    jito_tip_lamports: Optional[int] = None
    oco_payload: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
