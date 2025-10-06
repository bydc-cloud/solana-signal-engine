"""
Telegram Command Router
Routes incoming Telegram commands to appropriate handlers
"""
import logging
from typing import Dict
from datetime import datetime, timedelta

from aura.database import db
from aura.telegram_bot import telegram_bot

logger = logging.getLogger(__name__)


class TelegramCommandRouter:
    """
    Routes Telegram commands to handlers
    Supports:
    - /prompt [text] → Forward to AURA
    - /panel edit [config] → Config MCP propose_patch
    - /approve [id] → Apply/merge/deploy patch
    - /report [today|week] → Generate digest
    - /status → System status
    - /scan → Trigger scanner
    """

    def __init__(self):
        self.commands = {
            "prompt": self.handle_prompt,
            "panel": self.handle_panel,
            "approve": self.handle_approve,
            "report": self.handle_report,
            "status": self.handle_status,
            "scan": self.handle_scan,
            "help": self.handle_help,
        }

    async def route_command(self, command: str, args: str) -> str:
        """
        Route command to handler
        Returns response message
        """
        try:
            handler = self.commands.get(command)

            if not handler:
                return f"❌ Unknown command: /{command}\n\nUse /help to see available commands."

            response = await handler(args)
            return response

        except Exception as e:
            logger.error(f"Command routing error: {e}")
            return f"❌ Error executing /{command}: {e}"

    async def handle_prompt(self, text: str) -> str:
        """
        /prompt [text]
        Forward text to AURA for processing
        """
        if not text:
            return "Usage: /prompt [your text]"

        # TODO: Integrate with AURA Claude interface
        # For now, just acknowledge
        return f"📝 Prompt received: {text}\n\nAURA will process this and respond."

    async def handle_panel(self, args: str) -> str:
        """
        /panel edit [key] [value]
        Propose a config patch for approval
        """
        parts = args.split(maxsplit=2)

        if len(parts) < 3:
            return "Usage: /panel edit [key] [value]\n\nExample: /panel edit scanner_signal_threshold 70"

        action = parts[0]
        key = parts[1]
        value = parts[2]

        if action != "edit":
            return f"❌ Unknown panel action: {action}\n\nSupported: edit"

        try:
            # Get current value
            old_value = db.get_config(key)

            if old_value is None:
                return f"❌ Config key not found: {key}"

            # Create patch (pending approval)
            with db._get_conn() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO config_patches (config_key, old_value, new_value, patch_type, applied)
                    VALUES (?, ?, ?, 'update', 0)
                """, (key, str(old_value), value))
                patch_id = cur.lastrowid
                conn.commit()

            return f"""📝 Config Patch Proposed

ID: {patch_id}
Key: `{key}`
Old Value: `{old_value}`
New Value: `{value}`

Use /approve {patch_id} to apply this change."""

        except Exception as e:
            return f"❌ Panel error: {e}"

    async def handle_approve(self, args: str) -> str:
        """
        /approve [patch_id]
        Apply a pending config patch
        """
        if not args:
            return "Usage: /approve [patch_id]"

        try:
            patch_id = int(args)

            with db._get_conn() as conn:
                cur = conn.cursor()

                # Get patch
                cur.execute("""
                    SELECT config_key, old_value, new_value, patch_type, applied
                    FROM config_patches
                    WHERE id = ?
                """, (patch_id,))

                row = cur.fetchone()

                if not row:
                    return f"❌ Patch {patch_id} not found"

                if row[4] == 1:
                    return f"✅ Patch {patch_id} already applied"

                key, old_value, new_value, patch_type = row[:4]

                # Apply patch
                db.set_config(key, new_value)

                # Mark as applied
                cur.execute("""
                    UPDATE config_patches
                    SET applied = 1, applied_at = datetime('now'), approved_by = 'telegram'
                    WHERE id = ?
                """, (patch_id,))
                conn.commit()

            return f"""✅ Patch Applied

ID: {patch_id}
Key: `{key}`
Old Value: `{old_value}`
New Value: `{new_value}`

Config updated successfully!"""

        except ValueError:
            return "❌ Invalid patch ID (must be a number)"
        except Exception as e:
            return f"❌ Approve error: {e}"

    async def handle_report(self, period: str) -> str:
        """
        /report [today|week]
        Generate performance digest
        """
        period = period.strip().lower() or "today"

        if period not in ["today", "week"]:
            return "Usage: /report [today|week]"

        try:
            # Calculate time range
            if period == "today":
                since = datetime.now() - timedelta(days=1)
                period_name = "Last 24 Hours"
            else:
                since = datetime.now() - timedelta(days=7)
                period_name = "Last 7 Days"

            since_str = since.isoformat()

            with db._get_conn() as conn:
                cur = conn.cursor()

                # Get signals
                cur.execute("""
                    SELECT COUNT(*) FROM helix_signals
                    WHERE created_at >= ?
                """, (since_str,))
                signals_count = cur.fetchone()[0]

                # Get trades
                cur.execute("""
                    SELECT COUNT(*), SUM(pnl_usd), AVG(pnl_percent)
                    FROM trades
                    WHERE opened_at >= ?
                """, (since_str,))
                trades_row = cur.fetchone()
                trades_count = trades_row[0] or 0
                total_pnl = trades_row[1] or 0
                avg_pnl_pct = trades_row[2] or 0

                # Get alerts
                cur.execute("""
                    SELECT COUNT(*) FROM alerts
                    WHERE created_at >= ?
                """, (since_str,))
                alerts_count = cur.fetchone()[0]

                # Top movers
                cur.execute("""
                    SELECT symbol, momentum_score
                    FROM helix_signals
                    WHERE created_at >= ?
                    ORDER BY momentum_score DESC
                    LIMIT 5
                """, (since_str,))
                top_movers = cur.fetchall()

            # Format report
            report = f"""📊 *AURA Performance Report - {period_name}*

*Key Metrics:*
📡 Signals: `{signals_count}`
💼 Trades: `{trades_count}`
💰 Total P&L: `${total_pnl:,.2f}`
📈 Avg P&L: `{avg_pnl_pct:.2f}%`
🔔 Alerts: `{alerts_count}`

"""

            if top_movers:
                report += "*Top Movers:*\n"
                for symbol, momentum in top_movers:
                    report += f"• `{symbol}`: {momentum:.1f} momentum\n"

            report += f"\n_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_"

            return report

        except Exception as e:
            return f"❌ Report error: {e}"

    async def handle_status(self, args: str) -> str:
        """
        /status
        Show current system status
        """
        try:
            stats = db.get_system_stats()

            message = f"""📊 *System Status*

🎯 Tokens Tracked: `{stats.get('tokens_tracked', 0)}`
👀 Watchlist: `{stats.get('watchlist_count', 0)}`
💼 Open Positions: `{stats.get('open_positions', 0)}`
📈 Active Strategies: `{stats.get('active_strategies', 0)}`
🔔 Unread Alerts: `{stats.get('unread_alerts', 0)}`

⚙️ Paper Trading: `{'✅' if db.get_config('paper_trading_enabled') else '❌'}`
🔄 Auto Watchlist: `{'✅' if db.get_config('auto_watchlist_enabled') else '❌'}`

_Status checked: {datetime.now().strftime('%H:%M:%S')}_"""

            return message

        except Exception as e:
            return f"❌ Status error: {e}"

    async def handle_scan(self, args: str) -> str:
        """
        /scan
        Trigger manual scanner cycle
        """
        try:
            from aura.autonomous import autonomous_engine

            # Trigger signal processing
            processed = autonomous_engine.process_new_signals()

            return f"""🔍 *Scanner Triggered*

Processed: `{processed}` new signals

Scanner will continue running automatically every 30 seconds."""

        except Exception as e:
            return f"❌ Scan error: {e}"

    async def handle_help(self, args: str) -> str:
        """
        /help
        Show available commands
        """
        return """🤖 *AURA Telegram Commands*

*Trading & Monitoring:*
/status - System status
/scan - Trigger manual scan
/report [today|week] - Performance report

*Configuration:*
/panel edit [key] [value] - Propose config change
/approve [id] - Apply pending patch

*AI Interaction:*
/prompt [text] - Send prompt to AURA

*Other Commands:*
/portfolio - Portfolio summary
/watchlist - Show watchlist
/signals - Recent signals
/strategies - Active strategies
/help - Show this help

_AURA is running autonomously 24/7 🚀_"""


# Singleton
telegram_router = TelegramCommandRouter()
