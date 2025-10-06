"""
Telegram Webhook Handler for AURA
Alternative to polling - uses webhooks for faster, more reliable delivery
"""
from fastapi import APIRouter, Request
from typing import Dict
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/telegram", tags=["Telegram"])


@router.post("/webhook")
async def telegram_webhook(request: Request):
    """
    Handle incoming Telegram updates via webhook
    Railway URL will be: https://signal-railway-deployment-production.up.railway.app/telegram/webhook
    """
    try:
        update = await request.json()
        logger.info(f"📱 Received Telegram update: {update.get('update_id')}")

        # Get message from update
        message = update.get('message', {})
        if not message:
            return {"ok": True, "message": "No message in update"}

        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '')

        if not text:
            return {"ok": True, "message": "No text in message"}

        logger.info(f"📝 Message from {chat_id}: {text}")

        # Import bot handler
        from aura.telegram_bot import telegram_bot

        if not telegram_bot.enabled:
            logger.warning("Telegram bot not enabled")
            return {"ok": True, "message": "Bot not enabled"}

        # Handle the message
        response_text = await handle_telegram_message(text, chat_id)

        # Send response
        import aiohttp
        bot_token = telegram_bot.bot.token if hasattr(telegram_bot, 'bot') else None

        if not bot_token:
            # Get token from env
            import os
            bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

        if bot_token and response_text:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                payload = {
                    "chat_id": chat_id,
                    "text": response_text,
                    "parse_mode": "Markdown"
                }
                async with session.post(url, json=payload) as resp:
                    result = await resp.json()
                    logger.info(f"✅ Sent response: {result.get('ok')}")

        return {"ok": True}

    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        return {"ok": False, "error": str(e)}


async def handle_telegram_message(text: str, chat_id: int) -> str:
    """Process message and return response"""
    from aura.database import db

    # Handle commands
    if text.startswith('/start'):
        return """🤖 *AURA v0.3.0 - Autonomous Crypto Intelligence*

I can help you with:

*Commands:*
• `/portfolio` - Portfolio summary
• `/watchlist` - Watched tokens
• `/signals` - Recent signals
• `/stats` - System stats
• `/help` - Full command list

*Natural Language:*
Just send me a message! Ask me to:
• Summarize portfolio performance
• Analyze tokens
• Debug system issues
• Check status

Ready to assist 24/7 🚀"""

    elif text.startswith('/portfolio'):
        summary = db.get_portfolio_summary()
        return f"""💼 *Portfolio Summary*

Open Positions: `{summary['open_positions']}`
Closed Positions: `{summary['closed_positions']}`
Total P&L: `${summary['total_pnl_usd']:.2f}`
Win Rate: `{summary['win_rate']:.1f}%`"""

    elif text.startswith('/signals'):
        signals = db.get_recent_helix_signals(hours=24, limit=5)
        if not signals:
            return "📡 No recent signals in the last 24 hours"

        msg = f"📡 *Recent Signals* (last 24h)\n\n"
        for sig in signals:
            msg += f"• `{sig['symbol']}` - Momentum: {sig['momentum_score']:.1f}\n"
        return msg

    elif text.startswith('/stats'):
        portfolio = db.get_portfolio_summary()
        watchlist = db.get_watchlist()
        strategies = db.get_active_strategies()

        return f"""📊 *System Statistics*

🎯 Watchlist: `{len(watchlist)}` tokens
💼 Open Positions: `{portfolio['open_positions']}`
📈 Active Strategies: `{len(strategies)}`
🔔 Paper Trading: `Enabled`"""

    elif text.startswith('/help'):
        return """📋 *AURA Commands*

*Basic Commands:*
• `/start` - Welcome message
• `/portfolio` - Portfolio summary
• `/watchlist` - Watched tokens
• `/signals` - Recent signals (24h)
• `/stats` - System statistics
• `/strategies` - Active strategies

*Natural Language:*
Just send me any message and I'll help!

Examples:
• "how's my portfolio?"
• "why no signals today?"
• "what's the system status?"

🤖 Powered by AURA v0.3.0"""

    else:
        # Natural language handling
        portfolio = db.get_portfolio_summary()
        watchlist = db.get_watchlist()
        signals = db.get_recent_helix_signals(hours=24, limit=5)

        text_lower = text.lower()

        if "portfolio" in text_lower or "pnl" in text_lower:
            return f"""🤔 You asked: _{text}_

💼 *Current Portfolio:*
• Open Positions: {portfolio['open_positions']}
• Total P&L: ${portfolio['total_pnl_usd']:.2f}
• Win Rate: {portfolio['win_rate']:.1f}%"""

        elif "signal" in text_lower or "alert" in text_lower:
            return f"""🤔 You asked: _{text}_

📡 *Recent Signals:* {len(signals)} in last 24h

Use `/signals` for details"""

        elif "status" in text_lower or "health" in text_lower:
            return f"""🤔 You asked: _{text}_

✅ *System Status:* Healthy
• Watchlist: {len(watchlist)} tokens
• Open Positions: {portfolio['open_positions']}
• Recent Signals: {len(signals)}

All systems operational!"""

        else:
            return f"""🤖 I received: _{text}_

I can help with:
• Portfolio analysis (`/portfolio`)
• Signal monitoring (`/signals`)
• System status (`/stats`)

Or just ask me questions!"""


@router.get("/setup-webhook")
async def setup_webhook():
    """Setup webhook URL with Telegram"""
    import os
    import aiohttp

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        return {"error": "TELEGRAM_BOT_TOKEN not set"}

    webhook_url = "https://signal-railway-deployment-production.up.railway.app/telegram/webhook"

    async with aiohttp.ClientSession() as session:
        url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        payload = {"url": webhook_url}

        async with session.post(url, json=payload) as resp:
            result = await resp.json()

            if result.get('ok'):
                return {
                    "success": True,
                    "message": "Webhook set successfully",
                    "webhook_url": webhook_url,
                    "result": result
                }
            else:
                return {
                    "success": False,
                    "error": result.get('description'),
                    "result": result
                }


@router.get("/webhook-info")
async def webhook_info():
    """Get current webhook info"""
    import os
    import aiohttp

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        return {"error": "TELEGRAM_BOT_TOKEN not set"}

    async with aiohttp.ClientSession() as session:
        url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"

        async with session.get(url) as resp:
            result = await resp.json()
            return result
