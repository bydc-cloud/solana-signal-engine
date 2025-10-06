"""
AURA Telegram Bot
Notifications and interactive commands via Telegram
Requires: pip install python-telegram-bot
"""
import os
import logging
import asyncio
from typing import Dict
from datetime import datetime

logger = logging.getLogger(__name__)

# Telegram configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Lazy import database to avoid circular imports
_db = None
def get_db():
    global _db
    if _db is None:
        from .database import db
        _db = db
    return _db

class AuraTelegramBot:
    """
    Telegram bot for AURA notifications and commands
    Commands:
    - /portfolio - Show portfolio summary
    - /watchlist - Show watchlist
    - /signals - Show recent signals
    - /stats - Show system stats
    - /strategies - Show active strategies
    """

    def __init__(self):
        self.enabled = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)
        self.bot = None

        if self.enabled:
            try:
                from telegram import Bot
                self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
                logger.info("✅ Telegram bot initialized")
            except ImportError:
                logger.warning("⚠️  python-telegram-bot not installed. Run: pip install python-telegram-bot")
                self.enabled = False
            except Exception as e:
                logger.error(f"❌ Telegram bot init error: {e}")
                self.enabled = False

    async def send_message(self, message: str, parse_mode: str = "Markdown") -> bool:
        """Send message to Telegram"""
        if not self.enabled:
            logger.debug(f"Telegram disabled, would send: {message}")
            return False

        try:
            await self.bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=message,
                parse_mode=parse_mode
            )
            return True
        except Exception as e:
            logger.error(f"Telegram send error: {e}")
            return False

    async def send_alert(self, title: str, message: str, priority: str = "medium") -> bool:
        """Send formatted alert"""
        emoji_map = {
            "low": "ℹ️",
            "medium": "⚠️",
            "high": "🚨",
            "critical": "🔥"
        }

        emoji = emoji_map.get(priority, "📢")
        formatted = f"{emoji} *{title}*\n\n{message}\n\n_Time: {datetime.now().strftime('%H:%M:%S')}_"

        return await self.send_message(formatted)

    async def send_signal(self, symbol: str, momentum: float, details: Dict) -> bool:
        """Send trading signal notification"""
        message = f"""
🎯 *New Signal: {symbol}*

Momentum: `{momentum:.1f}`
Market Cap: `${details.get('mc', 0):,.0f}`
Liquidity: `${details.get('liquidity', 0):,.0f}`
Volume Ratio: `{details.get('volume_ratio', 0):.2f}`

[View on Birdeye](https://birdeye.so/token/{details.get('address', '')})
"""
        return await self.send_message(message)

    async def send_trade(self, action: str, symbol: str, price: float, amount: float, reason: str) -> bool:
        """Send trade execution notification"""
        emoji = "🟢" if action.lower() == "buy" else "🔴"
        message = f"""
{emoji} *{action.upper()}: {symbol}*

Price: `${price:.6f}`
Amount: `{amount:,.2f}`
Value: `${price * amount:,.2f}`

Reason: {reason}
"""
        return await self.send_message(message)

    async def send_portfolio_summary(self, summary: Dict) -> bool:
        """Send portfolio summary"""
        message = f"""
💼 *Portfolio Summary*

Open Positions: `{summary['open_positions']}`
Portfolio Value: `${summary['open_value_usd']:,.2f}`
Total P&L: `${summary['total_pnl_usd']:,.2f}`
Win Rate: `{summary['win_rate']:.1f}%`
Closed Trades: `{summary['closed_positions']}`
"""
        return await self.send_message(message)

    async def setup_commands(self):
        """
        Setup bot command handlers
        """
        if not self.enabled:
            return

        try:
            from telegram.ext import Application, CommandHandler

            # Create application
            self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

            # Add command handlers
            self.application.add_handler(CommandHandler("portfolio", self.cmd_portfolio))
            self.application.add_handler(CommandHandler("watchlist", self.cmd_watchlist))
            self.application.add_handler(CommandHandler("signals", self.cmd_signals))
            self.application.add_handler(CommandHandler("stats", self.cmd_stats))
            self.application.add_handler(CommandHandler("strategies", self.cmd_strategies))
            self.application.add_handler(CommandHandler("help", self.cmd_help))

            # Add new router commands
            self.application.add_handler(CommandHandler("prompt", self.cmd_prompt))
            self.application.add_handler(CommandHandler("panel", self.cmd_panel))
            self.application.add_handler(CommandHandler("approve", self.cmd_approve))
            self.application.add_handler(CommandHandler("report", self.cmd_report))
            self.application.add_handler(CommandHandler("scan", self.cmd_scan))

            # Start bot in background
            asyncio.create_task(self.application.run_polling())
            logger.info("✅ Telegram command handlers registered")

        except Exception as e:
            logger.error(f"Setup commands error: {e}")

    async def cmd_portfolio(self, update, context):
        """Handle /portfolio command"""
        try:
            db = get_db()
            summary = db.get_portfolio_summary()
            positions = db.get_open_positions()

            message = f"""💼 *Portfolio Summary*

📊 Open Positions: `{summary['open_positions']}`
💰 Portfolio Value: `${summary['open_value_usd']:,.2f}`
📈 Total P&L: `${summary['total_pnl_usd']:,.2f}` (`{summary['total_pnl_percent']:.2f}%`)
🎯 Win Rate: `{summary['win_rate']:.1f}%`

*Open Positions:*
"""
            for pos in positions[:5]:  # Show top 5
                message += f"\n• {pos['symbol']}: ${pos['current_value_usd']:,.2f} ({pos['pnl_percent']:+.1f}%)"

            await update.message.reply_text(message, parse_mode='Markdown')

        except Exception as e:
            await update.message.reply_text(f"Error: {e}")

    async def cmd_watchlist(self, update, context):
        """Handle /watchlist command"""
        try:
            db = get_db()
            watchlist = db.get_watchlist()

            if not watchlist:
                await update.message.reply_text("👀 Watchlist is empty")
                return

            message = f"👀 *Watchlist* ({len(watchlist)} tokens)\n\n"

            for item in watchlist[:10]:  # Show top 10
                message += f"• `{item['symbol']}` - {item['reason']}\n"

            await update.message.reply_text(message, parse_mode='Markdown')

        except Exception as e:
            await update.message.reply_text(f"Error: {e}")

    async def cmd_signals(self, update, context):
        """Handle /signals command"""
        try:
            db = get_db()
            signals = db.get_recent_helix_signals(hours=24, limit=10)

            if not signals:
                await update.message.reply_text("📡 No recent signals")
                return

            message = f"📡 *Recent Signals* (last 24h)\n\n"

            for signal in signals:
                momentum = signal.get('momentum_score', 0)
                message += f"• `{signal['symbol']}` - Momentum: {momentum:.1f}\n"

            await update.message.reply_text(message, parse_mode='Markdown')

        except Exception as e:
            await update.message.reply_text(f"Error: {e}")

    async def cmd_stats(self, update, context):
        """Handle /stats command"""
        try:
            db = get_db()
            stats = db.get_system_stats()

            message = f"""📊 *System Statistics*

🎯 Tokens Tracked: `{stats.get('tokens_tracked', 0)}`
👀 Watchlist: `{stats.get('watchlist_count', 0)}`
💼 Open Positions: `{stats.get('open_positions', 0)}`
📈 Active Strategies: `{stats.get('active_strategies', 0)}`
🔔 Unread Alerts: `{stats.get('unread_alerts', 0)}`

⚙️ Paper Trading: `{'✅ Enabled' if db.get_config('paper_trading_enabled') else '❌ Disabled'}`
🔄 Auto Watchlist: `{'✅ Enabled' if db.get_config('auto_watchlist_enabled') else '❌ Disabled'}`
"""
            await update.message.reply_text(message, parse_mode='Markdown')

        except Exception as e:
            await update.message.reply_text(f"Error: {e}")

    async def cmd_strategies(self, update, context):
        """Handle /strategies command"""
        try:
            db = get_db()
            strategies = db.get_active_strategies()

            if not strategies:
                await update.message.reply_text("🤖 No active strategies")
                return

            message = f"🤖 *Active Strategies* ({len(strategies)})\n\n"

            for strat in strategies:
                message += f"• *{strat['name']}*\n"
                message += f"  Type: `{strat['type']}`\n"
                message += f"  Capital: `${strat.get('capital_allocation_usd', 0):,.0f}`\n\n"

            await update.message.reply_text(message, parse_mode='Markdown')

        except Exception as e:
            await update.message.reply_text(f"Error: {e}")

    async def cmd_help(self, update, context):
        """Handle /help command"""
        from telegram_command_router import telegram_router
        response = await telegram_router.handle_help("")
        await update.message.reply_text(response, parse_mode='Markdown')

    async def cmd_prompt(self, update, context):
        """Handle /prompt command"""
        from telegram_command_router import telegram_router
        text = " ".join(context.args) if context.args else ""
        response = await telegram_router.route_command("prompt", text)
        await update.message.reply_text(response, parse_mode='Markdown')

    async def cmd_panel(self, update, context):
        """Handle /panel command"""
        from telegram_command_router import telegram_router
        args = " ".join(context.args) if context.args else ""
        response = await telegram_router.route_command("panel", args)
        await update.message.reply_text(response, parse_mode='Markdown')

    async def cmd_approve(self, update, context):
        """Handle /approve command"""
        from telegram_command_router import telegram_router
        args = " ".join(context.args) if context.args else ""
        response = await telegram_router.route_command("approve", args)
        await update.message.reply_text(response, parse_mode='Markdown')

    async def cmd_report(self, update, context):
        """Handle /report command"""
        from telegram_command_router import telegram_router
        args = " ".join(context.args) if context.args else "today"
        response = await telegram_router.route_command("report", args)
        await update.message.reply_text(response, parse_mode='Markdown')

    async def cmd_scan(self, update, context):
        """Handle /scan command"""
        from telegram_command_router import telegram_router
        response = await telegram_router.route_command("scan", "")
        await update.message.reply_text(response, parse_mode='Markdown')


# Singleton
telegram_bot = AuraTelegramBot()
