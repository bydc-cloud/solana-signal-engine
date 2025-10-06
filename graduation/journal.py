
"""Database journaling for Graduation."""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from .types import EnrichedCandidate, ExecutionReport, GateResult, ModelOutput, ScoringResult, SizingDecision

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).resolve().parent.parent / "final_nuclear.db"

MIGRATIONS = [
    """
    CREATE TABLE IF NOT EXISTS alerts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token_address TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        payload TEXT
    )
    """.strip(),
    """
    CREATE TABLE IF NOT EXISTS trades(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token_address TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        metadata TEXT
    )
    """.strip(),
    "ALTER TABLE alerts ADD COLUMN grad_ev_on_risk REAL",
    "ALTER TABLE alerts ADD COLUMN grad_probs TEXT",
    "ALTER TABLE alerts ADD COLUMN grad_gs REAL",
    "ALTER TABLE alerts ADD COLUMN grad_mode TEXT",
    "ALTER TABLE trades ADD COLUMN grad_size_fraction REAL",
    "ALTER TABLE trades ADD COLUMN grad_route TEXT",
    "ALTER TABLE trades ADD COLUMN grad_slippage_bps INTEGER",
    "ALTER TABLE trades ADD COLUMN grad_jito_tip_lamports INTEGER",
    "ALTER TABLE trades ADD COLUMN grad_oco_json TEXT",
    """
    CREATE TABLE IF NOT EXISTS grad_paper_equity(
        ts TEXT DEFAULT CURRENT_TIMESTAMP,
        equity_usd REAL,
        open_exposure REAL,
        realized_pnl_usd REAL,
        unrealized_pnl_usd REAL
    )
    """.strip(),
    """
    CREATE TABLE IF NOT EXISTS grad_blocklists(
        creator_addr TEXT PRIMARY KEY,
        reason TEXT,
        added_ts TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """.strip(),
    """
    CREATE TABLE IF NOT EXISTS grad_lockers(
        addr TEXT PRIMARY KEY,
        reputation REAL,
        notes TEXT
    )
    """.strip(),
]


def apply_migrations() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        for stmt in MIGRATIONS:
            try:
                cur.execute(stmt)
            except sqlite3.OperationalError as exc:
                if "duplicate column" in str(exc).lower():
                    continue
                logger.error("Migration failed for %s: %s", stmt, exc)
        conn.commit()


def journal_alert(candidate: EnrichedCandidate, scoring: ScoringResult, probs: ModelOutput, decision: SizingDecision, gate_result: GateResult) -> None:
    payload = {
        "address": candidate.address,
        "symbol": candidate.symbol,
        "gs": scoring.gs,
        "probs": probs.as_dict(),
        "mode": decision.mode,
        "ev": decision.ev,
        "gates": {c.name: c.passed for c in gate_result.checks},
        "timestamp": datetime.utcnow().isoformat(),
    }
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO alerts(token_address, payload, grad_ev_on_risk, grad_probs, grad_gs, grad_mode) VALUES(?,?,?,?,?,?)",
            (
                candidate.address,
                json.dumps(payload),
                decision.ev,
                json.dumps(probs.as_dict()),
                scoring.gs,
                decision.mode,
            ),
        )
        conn.commit()


def journal_trade(candidate: EnrichedCandidate, decision: SizingDecision, report: ExecutionReport) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO trades(token_address, grad_size_fraction, grad_route, grad_slippage_bps, grad_jito_tip_lamports, grad_oco_json, metadata) VALUES(?,?,?,?,?,?,?)",
            (
                candidate.address,
                decision.size_fraction,
                report.route,
                report.slippage_bps,
                report.jito_tip_lamports,
                json.dumps(report.oco_payload or {}),
                json.dumps({"txid": report.txid, "mode": decision.mode}),
            ),
        )
        conn.commit()


def journal_paper_equity(snapshot: Dict[str, Any]) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO grad_paper_equity(equity_usd, open_exposure, realized_pnl_usd, unrealized_pnl_usd) VALUES(?,?,?,?)",
            (
                snapshot.get("paper_equity"),
                snapshot.get("open_exposure"),
                snapshot.get("paper_realized"),
                snapshot.get("paper_unrealized"),
            ),
        )
        conn.commit()
