"""
AURA Chat Interface
Natural language queries and context-aware responses
"""
import logging
from typing import Dict, List
from .database import db
from .memory import memory

logger = logging.getLogger(__name__)


class AuraChat:
    """Natural language interface to AURA"""

    def __init__(self):
        self.db = db
        self.memory = memory

    def process_query(self, query: str) -> Dict:
        """Process natural language query"""
        query_lower = query.lower()

        # Portfolio queries
        if any(word in query_lower for word in ["portfolio", "positions", "holding"]):
            return self._handle_portfolio_query(query_lower)

        # Watchlist queries
        if any(word in query_lower for word in ["watchlist", "watching", "tracked"]):
            return self._handle_watchlist_query(query_lower)

        # Signal queries
        if any(word in query_lower for word in ["signal", "alert", "momentum"]):
            return self._handle_signal_query(query_lower)

        # Strategy queries
        if any(word in query_lower for word in ["strategy", "backtest", "performance"]):
            return self._handle_strategy_query(query_lower)

        # Stats queries
        if any(word in query_lower for word in ["stats", "summary", "overview"]):
            return self._handle_stats_query()

        # Default
        return {
            "type": "help",
            "message": "I can help you with: portfolio, watchlist, signals, strategies, stats",
            "suggestions": [
                "Show me my portfolio",
                "What's in my watchlist?",
                "Show recent signals",
                "How are my strategies performing?",
                "Give me system stats",
            ]
        }

    def _handle_portfolio_query(self, query: str) -> Dict:
        """Handle portfolio-related queries"""
        summary = self.db.get_portfolio_summary()
        open_positions = self.db.get_open_positions()

        if summary["open_positions"] == 0:
            message = "📊 Your portfolio is empty. No open positions."
        else:
            message = f"📊 Portfolio Summary:\n"
            message += f"• Open positions: {summary['open_positions']}\n"
            message += f"• Value: ${summary['open_value_usd']:,.2f}\n"
            message += f"• Total P&L: ${summary['total_pnl_usd']:,.2f}\n"
            message += f"• Win rate: {summary['win_rate']:.1f}%"

        return {
            "type": "portfolio",
            "message": message,
            "data": {
                "summary": summary,
                "open_positions": open_positions,
            }
        }

    def _handle_watchlist_query(self, query: str) -> Dict:
        """Handle watchlist-related queries"""
        watchlist = self.db.get_watchlist()

        if len(watchlist) == 0:
            message = "👁️ Your watchlist is empty."
        else:
            message = f"👁️ Watchlist ({len(watchlist)} tokens):\n"
            for item in watchlist[:5]:
                token = self.db.get_token(item["token_address"])
                symbol = token["symbol"] if token else "UNKNOWN"
                message += f"• {symbol}: {item['reason']}\n"

        return {
            "type": "watchlist",
            "message": message,
            "data": {"watchlist": watchlist}
        }

    def _handle_signal_query(self, query: str) -> Dict:
        """Handle signal-related queries"""
        signals = self.db.get_recent_helix_signals(hours=24, limit=10)

        if len(signals) == 0:
            message = "📡 No signals in the last 24 hours."
        else:
            message = f"📡 Recent Signals ({len(signals)}):\n"
            for sig in signals[:5]:
                message += f"• {sig['symbol']}: momentum {sig['momentum_score']:.1f}\n"

        return {
            "type": "signals",
            "message": message,
            "data": {"signals": signals}
        }

    def _handle_strategy_query(self, query: str) -> Dict:
        """Handle strategy-related queries"""
        strategies = self.db.get_active_strategies()

        if len(strategies) == 0:
            message = "🎯 No active strategies."
        else:
            message = f"🎯 Active Strategies ({len(strategies)}):\n"
            for strat in strategies:
                message += f"• {strat['name']}: {strat['type']}\n"

        return {
            "type": "strategies",
            "message": message,
            "data": {"strategies": strategies}
        }

    def _handle_stats_query(self) -> Dict:
        """Handle stats queries"""
        with self.db._get_conn() as conn:
            cur = conn.cursor()

            cur.execute("SELECT COUNT(*) FROM tokens")
            tokens = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM watchlist")
            watchlist_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM portfolio_items WHERE status = 'open'")
            open_pos = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM alert_history WHERE read = 0")
            unread = cur.fetchone()[0]

        signals = self.db.get_recent_helix_signals(hours=24, limit=10000)

        message = f"📈 System Stats:\n"
        message += f"• Tokens tracked: {tokens}\n"
        message += f"• Watchlist size: {watchlist_count}\n"
        message += f"• Open positions: {open_pos}\n"
        message += f"• Unread alerts: {unread}\n"
        message += f"• Signals (24h): {len(signals)}"

        return {
            "type": "stats",
            "message": message,
            "data": {
                "tokens_tracked": tokens,
                "watchlist_size": watchlist_count,
                "open_positions": open_pos,
                "unread_alerts": unread,
                "signals_24h": len(signals),
            }
        }


# Singleton
chat = AuraChat()
