"""
AURA Telegram Bot
Notifications and interactive commands via Telegram
Requires: pip install python-telegram-bot
"""
import os
import logging
from typing import Dict
from datetime import datetime

logger = logging.getLogger(__name__)

# Telegram configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

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


# Singleton
telegram_bot = AuraTelegramBot()
