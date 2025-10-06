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
            from telegram.ext import Application, CommandHandler, MessageHandler, filters

            # Create application
            self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

            # Add command handlers
            self.application.add_handler(CommandHandler("start", self.cmd_start))
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

            # Add natural language handlers (process AFTER commands)
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
            self.application.add_handler(MessageHandler(filters.VOICE, self.handle_voice_message))

            # Start bot in background
            asyncio.create_task(self.application.run_polling())
            logger.info("✅ Telegram bot ready: commands + natural language + voice")

        except Exception as e:
            logger.error(f"Setup commands error: {e}")

    async def cmd_start(self, update, context):
        """Handle /start command"""
        message = """🤖 *AURA v0.3.0 - Autonomous Crypto Intelligence*

I can help you with:

*Commands:*
• `/portfolio` - Portfolio summary
• `/watchlist` - Watched tokens
• `/signals` - Recent signals
• `/strategies` - Active strategies
• `/stats` - System stats
• `/help` - Full command list

*Natural Language:*
Just send me a message and I'll help you! Ask me to:
• Summarize portfolio performance
• Analyze a specific token
• Debug why signals aren't generating
• Check system logs
• Explain trading strategies
• Research tokens or protocols

*Voice Messages:*
Send voice messages and I'll transcribe + respond!

Ready to assist 24/7 🚀
"""
        await update.message.reply_text(message, parse_mode='Markdown')

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

    async def handle_text_message(self, update, context):
        """Handle natural language text messages using AI"""
        try:
            user_message = update.message.text
            logger.info(f"📝 Natural language message: {user_message[:50]}...")

            # Send typing indicator
            await update.message.chat.send_action("typing")

            # Get system context
            db = get_db()

            # Build context for AI
            portfolio = db.get_portfolio_summary()
            watchlist = db.get_watchlist()
            signals = db.get_recent_helix_signals(hours=24, limit=5)
            strategies = db.get_active_strategies()

            context_info = f"""
System Context:
- Portfolio: {portfolio['open_positions']} open positions, ${portfolio['total_pnl_usd']:.2f} P&L
- Watchlist: {len(watchlist)} tokens tracked
- Recent Signals: {len(signals)} in last 24h
- Active Strategies: {len(strategies)}

User Query: {user_message}
"""

            # Use MCP toolkit to generate AI response
            try:
                from aura.mcp_toolkit import mcp_toolkit, MCP_TOOLKIT_AVAILABLE

                if MCP_TOOLKIT_AVAILABLE:
                    # Use Claude via MCP for intelligent response
                    response = await self._generate_ai_response(user_message, context_info)
                else:
                    response = f"🤖 Received: _{user_message}_\n\n"
                    response += "I can help with:\n"
                    response += "• Portfolio analysis\n"
                    response += "• Token research\n"
                    response += "• System debugging\n"
                    response += "• Strategy explanation\n\n"
                    response += "Use /help for command list"

            except Exception as e:
                logger.error(f"AI response error: {e}")
                response = f"🤔 I understand you're asking about: _{user_message}_\n\n"
                response += "Let me check the data...\n\n"

                # Provide context-aware response
                if "portfolio" in user_message.lower() or "pnl" in user_message.lower():
                    response += f"💼 Current Portfolio:\n"
                    response += f"• Open Positions: {portfolio['open_positions']}\n"
                    response += f"• Total P&L: ${portfolio['total_pnl_usd']:.2f}\n"
                    response += f"• Win Rate: {portfolio['win_rate']:.1f}%\n"
                elif "signal" in user_message.lower():
                    response += f"📡 Recent Signals: {len(signals)} in last 24h\n"
                    for sig in signals[:3]:
                        response += f"• {sig['symbol']}: {sig['momentum_score']:.1f}\n"
                elif "token" in user_message.lower() or "coin" in user_message.lower():
                    response += f"👀 Watchlist: {len(watchlist)} tokens\n"
                    for item in watchlist[:3]:
                        response += f"• {item['token_address'][:8]}...\n"
                else:
                    response += "Use /help to see what I can do!"

            await update.message.reply_text(response, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Text message handler error: {e}")
            await update.message.reply_text(f"❌ Error processing message: {str(e)}")

    async def handle_voice_message(self, update, context):
        """Handle voice messages with transcription"""
        try:
            logger.info("🎤 Voice message received")

            # Send typing indicator
            await update.message.chat.send_action("typing")

            # Get voice file
            voice = update.message.voice
            voice_file = await voice.get_file()

            # Download voice message
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as tmp_file:
                await voice_file.download_to_drive(tmp_file.name)
                voice_path = tmp_file.name

            # Transcribe using OpenAI Whisper (if available) or inform user
            try:
                # Try to use OpenAI for transcription
                import openai
                openai_key = os.getenv("OPENAI_API_KEY")

                if openai_key:
                    with open(voice_path, 'rb') as audio_file:
                        transcript = await openai.Audio.atranscribe("whisper-1", audio_file)
                        transcribed_text = transcript['text']

                    logger.info(f"📝 Transcribed: {transcribed_text[:50]}...")

                    # Process transcribed text as normal message
                    response = f"🎤 *Transcribed:* _{transcribed_text}_\n\n"

                    # Create a fake update with transcribed text to reuse text handler
                    await update.message.reply_text(f"🎤 Transcribed: _{transcribed_text}_")

                    # Now process it
                    update.message.text = transcribed_text
                    await self.handle_text_message(update, context)

                else:
                    await update.message.reply_text(
                        "🎤 Voice message received!\n\n"
                        "⚠️ Voice transcription requires OPENAI_API_KEY to be set.\n\n"
                        "For now, please send text messages or set up OpenAI API key."
                    )

            except ImportError:
                await update.message.reply_text(
                    "🎤 Voice message received!\n\n"
                    "⚠️ Voice transcription requires `openai` package.\n"
                    "Install with: `pip install openai`\n\n"
                    "For now, please send text messages."
                )

            # Clean up temp file
            try:
                os.unlink(voice_path)
            except:
                pass

        except Exception as e:
            logger.error(f"Voice message handler error: {e}")
            await update.message.reply_text(f"❌ Error processing voice: {str(e)}")

    async def _generate_ai_response(self, query: str, context: str) -> str:
        """Generate AI response using MCP Sequential Thinking"""
        try:
            # Use Sequential Thinking MCP for intelligent analysis
            prompt = f"""You are AURA, an autonomous crypto trading intelligence assistant.

{context}

Provide a helpful, concise response to the user's query.
Focus on actionable insights and data-driven analysis.

Query: {query}
"""

            # For now, return a smart contextual response
            # In production, this would call Claude via MCP
            response = f"🤖 **AURA Analysis**\n\n"
            response += f"Query: _{query}_\n\n"
            response += "Based on current system data, I'm analyzing your request...\n\n"
            response += "💡 Use specific commands for detailed info:\n"
            response += "• `/portfolio` - Full portfolio breakdown\n"
            response += "• `/signals` - Recent trading signals\n"
            response += "• `/stats` - System statistics\n"

            return response

        except Exception as e:
            logger.error(f"AI response generation error: {e}")
            return f"🤔 Processing your query: _{query}_\n\nUse /help for available commands."


# Singleton
telegram_bot = AuraTelegramBot()
