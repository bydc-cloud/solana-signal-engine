"""Learning analytics for graduation trades."""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).resolve().parent.parent / "final_nuclear.db"


def get_trade_stats(days: int = 1) -> Dict:
    """Get aggregated trade statistics for learning."""
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        # Total trades
        cur.execute("SELECT COUNT(*) FROM trades WHERE created_at >= ?", (cutoff,))
        total_trades = cur.fetchone()[0]

        # Trades by mode
        cur.execute("SELECT metadata FROM trades WHERE created_at >= ?", (cutoff,))
        rows = cur.fetchall()

        paper_trades = 0
        live_trades = 0
        for row in rows:
            try:
                meta = json.loads(row[0])
                if meta.get('mode') == 'PAPER':
                    paper_trades += 1
                elif meta.get('mode') == 'LIVE':
                    live_trades += 1
            except:
                pass

        # Alert stats
        cur.execute("SELECT COUNT(*) FROM alerts WHERE created_at >= ?", (cutoff,))
        total_alerts = cur.fetchone()[0]

        cur.execute("SELECT AVG(grad_gs), MIN(grad_gs), MAX(grad_gs) FROM alerts WHERE created_at >= ?", (cutoff,))
        gs_stats = cur.fetchone()

        # Paper equity
        cur.execute("SELECT equity_usd, realized_pnl_usd, unrealized_pnl_usd FROM grad_paper_equity ORDER BY ts DESC LIMIT 1")
        equity_row = cur.fetchone()

        stats = {
            'period_days': days,
            'total_trades': total_trades,
            'paper_trades': paper_trades,
            'live_trades': live_trades,
            'total_alerts': total_alerts,
            'avg_gs': round(gs_stats[0], 2) if gs_stats[0] else 0,
            'min_gs': round(gs_stats[1], 2) if gs_stats[1] else 0,
            'max_gs': round(gs_stats[2], 2) if gs_stats[2] else 0,
            'paper_equity_usd': round(equity_row[0], 2) if equity_row else 100000,
            'realized_pnl_usd': round(equity_row[1], 2) if equity_row and equity_row[1] else 0,
            'unrealized_pnl_usd': round(equity_row[2], 2) if equity_row and equity_row[2] else 0,
        }

        return stats


def get_recent_trades(limit: int = 10) -> List[Dict]:
    """Get recent trades for analysis."""
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                t.token_address,
                t.created_at,
                t.grad_size_fraction,
                t.grad_route,
                t.metadata,
                a.grad_gs,
                a.payload
            FROM trades t
            LEFT JOIN alerts a ON t.token_address = a.token_address
            ORDER BY t.created_at DESC
            LIMIT ?
        """, (limit,))

        trades = []
        for row in cur.fetchall():
            try:
                meta = json.loads(row[4]) if row[4] else {}
                payload = json.loads(row[6]) if row[6] else {}
                trades.append({
                    'address': row[0],
                    'created_at': row[1],
                    'size_fraction': row[2],
                    'route': row[3],
                    'mode': meta.get('mode'),
                    'txid': meta.get('txid'),
                    'gs': row[5],
                    'symbol': payload.get('symbol'),
                })
            except Exception as e:
                logger.debug(f"Error parsing trade: {e}")
                continue

        return trades


def print_daily_summary():
    """Print a summary of today's trading activity."""
    stats = get_trade_stats(days=1)

    print("\n" + "="*60)
    print("📊 DAILY LEARNING SUMMARY")
    print("="*60)
    print(f"Total Trades: {stats['total_trades']} (Paper: {stats['paper_trades']}, Live: {stats['live_trades']})")
    print(f"Total Alerts: {stats['total_alerts']}")
    print(f"Graduation Score: Avg {stats['avg_gs']}, Min {stats['min_gs']}, Max {stats['max_gs']}")
    print(f"Paper Equity: ${stats['paper_equity_usd']:,.2f}")
    print(f"Realized P&L: ${stats['realized_pnl_usd']:,.2f}")
    print(f"Unrealized P&L: ${stats['unrealized_pnl_usd']:,.2f}")
    print("="*60 + "\n")


if __name__ == "__main__":
    print_daily_summary()
    print("\nRecent Trades:")
    for trade in get_recent_trades(5):
        print(f"  {trade['created_at']} | {trade['symbol']} | GS:{trade['gs']:.1f} | {trade['mode']}")
