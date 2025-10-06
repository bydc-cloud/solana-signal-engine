"""
AURA Database Operations
Handles all database interactions for tokens, portfolio, watchlist, strategies, alerts
"""
import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from pathlib import Path

from . import AURA_DB_PATH, HELIX_DB_PATH


class AuraDB:
    """Main database interface for AURA"""

    def __init__(self, db_path: Path = AURA_DB_PATH):
        self.db_path = db_path

    def _get_conn(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    # ═══════════════════════════════════════════════════════════
    # TOKEN OPERATIONS
    # ═══════════════════════════════════════════════════════════

    def upsert_token(self, address: str, symbol: str, name: str, metadata: Dict) -> None:
        """Insert or update token"""
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO tokens (address, symbol, name, metadata, last_updated)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(address) DO UPDATE SET
                    symbol = excluded.symbol,
                    name = excluded.name,
                    metadata = excluded.metadata,
                    last_updated = excluded.last_updated
            """, (address, symbol, name, json.dumps(metadata), datetime.now().isoformat()))
            conn.commit()

    def get_token(self, address: str) -> Optional[Dict]:
        """Get token details"""
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT address, symbol, name, metadata, risk_score, sentiment_score, first_seen, last_updated
                FROM tokens WHERE address = ?
            """, (address,))
            row = cur.fetchone()
            if not row:
                return None
            return {
                "address": row[0],
                "symbol": row[1],
                "name": row[2],
                "metadata": json.loads(row[3]) if row[3] else {},
                "risk_score": row[4],
                "sentiment_score": row[5],
                "first_seen": row[6],
                "last_updated": row[7],
            }

    def add_token_fact(self, address: str, fact_type: str, fact: str, source: str, confidence: float = 0.8) -> None:
        """Add a fact about a token"""
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO token_facts (token_address, fact_type, fact, source, confidence)
                VALUES (?, ?, ?, ?, ?)
            """, (address, fact_type, fact, source, confidence))
            conn.commit()

    def get_token_facts(self, address: str, fact_type: Optional[str] = None) -> List[Dict]:
        """Get facts about a token"""
        with self._get_conn() as conn:
            cur = conn.cursor()
            if fact_type:
                cur.execute("""
                    SELECT id, fact_type, fact, source, confidence, created_at
                    FROM token_facts
                    WHERE token_address = ? AND fact_type = ?
                    ORDER BY created_at DESC
                """, (address, fact_type))
            else:
                cur.execute("""
                    SELECT id, fact_type, fact, source, confidence, created_at
                    FROM token_facts
                    WHERE token_address = ?
                    ORDER BY created_at DESC
                """, (address,))

            facts = []
            for row in cur.fetchall():
                facts.append({
                    "id": row[0],
                    "fact_type": row[1],
                    "fact": row[2],
                    "source": row[3],
                    "confidence": row[4],
                    "created_at": row[5],
                })
            return facts

    # ═══════════════════════════════════════════════════════════
    # PORTFOLIO OPERATIONS
    # ═══════════════════════════════════════════════════════════

    def add_position(self, token_address: str, entry_price: float, amount: float, notes: str = "") -> int:
        """Open a new position"""
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO portfolio_items (token_address, entry_price, amount, notes, status)
                VALUES (?, ?, ?, ?, 'open')
            """, (token_address, entry_price, amount, notes))
            conn.commit()
            return cur.lastrowid

    def close_position(self, position_id: int, exit_price: float) -> None:
        """Close a position"""
        with self._get_conn() as conn:
            cur = conn.cursor()
            # Get position details
            cur.execute("SELECT entry_price, amount FROM portfolio_items WHERE id = ?", (position_id,))
            row = cur.fetchone()
            if not row:
                return

            entry_price, amount = row
            pnl_usd = (exit_price - entry_price) * amount
            pnl_percent = ((exit_price / entry_price) - 1) * 100

            cur.execute("""
                UPDATE portfolio_items
                SET exit_price = ?, exit_time = ?, pnl_usd = ?, pnl_percent = ?, status = 'closed'
                WHERE id = ?
            """, (exit_price, datetime.now().isoformat(), pnl_usd, pnl_percent, position_id))
            conn.commit()

    def get_open_positions(self, user_id: int = 1) -> List[Dict]:
        """Get all open positions"""
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, token_address, entry_price, amount, entry_time, notes
                FROM portfolio_items
                WHERE user_id = ? AND status = 'open'
                ORDER BY entry_time DESC
            """, (user_id,))

            positions = []
            for row in cur.fetchall():
                positions.append({
                    "id": row[0],
                    "token_address": row[1],
                    "entry_price": row[2],
                    "amount": row[3],
                    "entry_time": row[4],
                    "notes": row[5],
                })
            return positions

    def get_portfolio_summary(self, user_id: int = 1) -> Dict:
        """Get portfolio summary stats"""
        with self._get_conn() as conn:
            cur = conn.cursor()

            # Open positions
            cur.execute("""
                SELECT COUNT(*), COALESCE(SUM(entry_price * amount), 0)
                FROM portfolio_items
                WHERE user_id = ? AND status = 'open'
            """, (user_id,))
            open_count, open_value = cur.fetchone()

            # Closed positions
            cur.execute("""
                SELECT COUNT(*), COALESCE(SUM(pnl_usd), 0), COALESCE(AVG(pnl_percent), 0)
                FROM portfolio_items
                WHERE user_id = ? AND status = 'closed'
            """, (user_id,))
            closed_count, total_pnl, avg_pnl_pct = cur.fetchone()

            # Win rate
            cur.execute("""
                SELECT COUNT(*) FROM portfolio_items
                WHERE user_id = ? AND status = 'closed' AND pnl_usd > 0
            """, (user_id,))
            winning_trades = cur.fetchone()[0]

            win_rate = (winning_trades / closed_count * 100) if closed_count > 0 else 0

            return {
                "open_positions": open_count,
                "open_value_usd": open_value,
                "closed_positions": closed_count,
                "total_pnl_usd": total_pnl,
                "avg_pnl_percent": avg_pnl_pct,
                "win_rate": win_rate,
            }

    # ═══════════════════════════════════════════════════════════
    # WATCHLIST OPERATIONS
    # ═══════════════════════════════════════════════════════════

    def add_to_watchlist(self, token_address: str, reason: str, alert_rules: Dict, user_id: int = 1) -> None:
        """Add token to watchlist"""
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR IGNORE INTO watchlist (user_id, token_address, reason, alert_rules)
                VALUES (?, ?, ?, ?)
            """, (user_id, token_address, reason, json.dumps(alert_rules)))
            conn.commit()

    def remove_from_watchlist(self, token_address: str, user_id: int = 1) -> None:
        """Remove token from watchlist"""
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                DELETE FROM watchlist WHERE user_id = ? AND token_address = ?
            """, (user_id, token_address))
            conn.commit()

    def get_watchlist(self, user_id: int = 1) -> List[Dict]:
        """Get all watched tokens"""
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, token_address, added_at, reason, alert_rules, triggered_count, last_triggered
                FROM watchlist
                WHERE user_id = ?
                ORDER BY added_at DESC
            """, (user_id,))

            watchlist = []
            for row in cur.fetchall():
                watchlist.append({
                    "id": row[0],
                    "token_address": row[1],
                    "added_at": row[2],
                    "reason": row[3],
                    "alert_rules": json.loads(row[4]) if row[4] else {},
                    "triggered_count": row[5],
                    "last_triggered": row[6],
                })
            return watchlist

    # ═══════════════════════════════════════════════════════════
    # STRATEGY OPERATIONS
    # ═══════════════════════════════════════════════════════════

    def get_active_strategies(self) -> List[Dict]:
        """Get all active strategies"""
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, name, description, type, rules, capital_allocation_usd, metrics
                FROM strategies
                WHERE status = 'active'
            """, ())

            strategies = []
            for row in cur.fetchall():
                strategies.append({
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "type": row[3],
                    "rules": json.loads(row[4]) if row[4] else {},
                    "capital_allocation_usd": row[5],
                    "metrics": json.loads(row[6]) if row[6] else {},
                })
            return strategies

    def add_strategy_trade(self, strategy_id: int, token_address: str, side: str,
                          price: float, amount: float, reason: str = "") -> int:
        """Record a strategy trade"""
        with self._get_conn() as conn:
            cur = conn.cursor()
            amount_usd = price * amount
            cur.execute("""
                INSERT INTO strategy_trades (strategy_id, token_address, side, price, amount, amount_usd, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (strategy_id, token_address, side, price, amount, amount_usd, reason))
            conn.commit()
            return cur.lastrowid

    def update_strategy_metrics(self, strategy_id: int, metrics: Dict) -> None:
        """Update strategy performance metrics"""
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE strategies
                SET metrics = ?, updated_at = ?
                WHERE id = ?
            """, (json.dumps(metrics), datetime.now().isoformat(), strategy_id))
            conn.commit()

    # ═══════════════════════════════════════════════════════════
    # ALERT OPERATIONS
    # ═══════════════════════════════════════════════════════════

    def create_alert(self, token_address: str, message: str, priority: str = "medium",
                    config_id: Optional[int] = None, metadata: Optional[Dict] = None) -> int:
        """Create a new alert"""
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO alert_history (config_id, token_address, message, priority, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (config_id, token_address, message, priority, json.dumps(metadata) if metadata else None))
            conn.commit()
            return cur.lastrowid

    def get_unread_alerts(self, limit: int = 50) -> List[Dict]:
        """Get unread alerts"""
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, token_address, triggered_at, message, priority, metadata
                FROM alert_history
                WHERE read = 0
                ORDER BY triggered_at DESC
                LIMIT ?
            """, (limit,))

            alerts = []
            for row in cur.fetchall():
                alerts.append({
                    "id": row[0],
                    "token_address": row[1],
                    "triggered_at": row[2],
                    "message": row[3],
                    "priority": row[4],
                    "metadata": json.loads(row[5]) if row[5] else {},
                })
            return alerts

    def mark_alert_read(self, alert_id: int) -> None:
        """Mark alert as read"""
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE alert_history SET read = 1 WHERE id = ?", (alert_id,))
            conn.commit()

    # ═══════════════════════════════════════════════════════════
    # CONFIG OPERATIONS
    # ═══════════════════════════════════════════════════════════

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get config value"""
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT value FROM system_configs WHERE key = ?", (key,))
            row = cur.fetchone()
            if not row:
                return default
            value = row[0]
            # Try to convert to appropriate type
            if value.lower() in ('true', 'false'):
                return value.lower() == 'true'
            try:
                return int(value)
            except ValueError:
                try:
                    return float(value)
                except ValueError:
                    return value

    def set_config(self, key: str, value: Any) -> None:
        """Set config value"""
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO system_configs (key, value, updated_at)
                VALUES (?, ?, ?)
            """, (key, str(value), datetime.now().isoformat()))
            conn.commit()

    def get_all_configs(self) -> Dict:
        """Get all configs"""
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT key, value, description FROM system_configs")
            configs = {}
            for row in cur.fetchall():
                key, value, desc = row
                # Try to convert to appropriate type
                if value.lower() in ('true', 'false'):
                    value = value.lower() == 'true'
                else:
                    try:
                        value = int(value)
                    except ValueError:
                        try:
                            value = float(value)
                        except ValueError:
                            pass
                configs[key] = {"value": value, "description": desc}
            return configs

    # ═══════════════════════════════════════════════════════════
    # HELIX SCANNER INTEGRATION
    # ═══════════════════════════════════════════════════════════

    def get_recent_helix_signals(self, hours: int = 24, limit: int = 100) -> List[Dict]:
        """Get recent signals from Helix scanner"""
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()

        with sqlite3.connect(HELIX_DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, token_address, symbol, created_at, grad_gs, payload
                FROM alerts
                WHERE created_at >= ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (cutoff, limit))

            signals = []
            for row in cur.fetchall():
                try:
                    payload = json.loads(row[5]) if row[5] else {}
                except:
                    payload = {}

                signals.append({
                    "id": row[0],
                    "token_address": row[1],
                    "symbol": row[2],
                    "created_at": row[3],
                    "momentum_score": row[4],
                    "payload": payload,
                })
            return signals


# Singleton instance
db = AuraDB()
