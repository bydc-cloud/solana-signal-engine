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
        # Calculate token age if created_at available
        age_str = ""
        if details.get('created_at'):
            from datetime import datetime
            try:
                created = datetime.fromisoformat(details['created_at'].replace('Z', '+00:00'))
                age_hours = (datetime.now() - created).total_seconds() / 3600
                if age_hours < 24:
                    age_str = f"\nAge: `{age_hours:.1f}h`"
                else:
                    age_days = age_hours / 24
                    age_str = f"\nAge: `{age_days:.1f}d`"
            except:
                pass

        # Clean formatting with minimal emojis
        message = f"""*New Signal: {symbol}*

Momentum: `{momentum:.1f}`
Market Cap: `${details.get('mc', 0):,.0f}`
Liquidity: `${details.get('liquidity', 0):,.0f}`
Volume: `${details.get('volume_24h', 0):,.0f}`{age_str}

[Dexscreener](https://dexscreener.com/solana/{details.get('address', '')}) • [Birdeye](https://birdeye.so/token/{details.get('address', '')})
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
        """Handle /watchlist command with token images"""
        try:
            db = get_db()
            watchlist = db.get_watchlist()

            if not watchlist:
                await update.message.reply_text("Watchlist is empty")
                return

            # Send a photo with the first token if available
            if watchlist and watchlist[0].get('token_address'):
                first_token = watchlist[0]
                address = first_token.get('token_address', '')
                symbol = first_token.get('symbol', 'Unknown')

                # Try to get token image from Dexscreener
                image_url = f"https://dd.dexscreener.com/ds-data/tokens/solana/{address}.png"

                try:
                    from telegram import InputMediaPhoto
                    await update.message.reply_photo(
                        photo=image_url,
                        caption=f"*{symbol}*\n[View on Dexscreener](https://dexscreener.com/solana/{address})",
                        parse_mode='Markdown'
                    )
                except:
                    pass  # If image fails, continue with text

            message = f"*Watchlist* ({len(watchlist)} tokens)\n\n"

            for item in watchlist[:10]:  # Show top 10
                symbol = item.get('symbol', 'Unknown')
                address = item.get('token_address', '')
                reason = item.get('reason', 'No reason')

                # Add Dexscreener link
                dex_link = f"https://dexscreener.com/solana/{address}"
                message += f"• [{symbol}]({dex_link}) - {reason}\n"

            message += f"\n💡 Click token symbols to view on Dexscreener"

            await update.message.reply_text(message, parse_mode='Markdown', disable_web_page_preview=True)

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
        """Handle natural language text messages using AI with command execution and memory"""
        try:
            user_message = update.message.text
            user_id = update.message.from_user.id
            username = update.message.from_user.username or update.message.from_user.first_name

            logger.info(f"📝 Natural language message from {username}: {user_message[:50]}...")

            # Send typing indicator
            await update.message.chat.send_action("typing")

            # Get system context
            db = get_db()

            # Build context for AI
            portfolio = db.get_portfolio_summary()
            watchlist = db.get_watchlist()
            signals = db.get_recent_helix_signals(hours=24, limit=5)
            strategies = db.get_active_strategies()

            # Store user interaction in memory (create entity if first time)
            try:
                await self._store_conversation_memory(user_id, username, user_message, portfolio, signals, watchlist)
            except Exception as e:
                logger.warning(f"Memory storage error: {e}")

            context_info = f"""
System Context:
- User: {username} (ID: {user_id})
- Portfolio: {portfolio['open_positions']} open positions, ${portfolio['total_pnl_usd']:.2f} P&L, {portfolio['win_rate']:.1f}% win rate
- Watchlist: {len(watchlist)} tokens tracked
- Recent Signals: {len(signals)} in last 24h
- Active Strategies: {len(strategies)}
- Available Commands: /portfolio, /watchlist, /signals, /strategies, /stats, /scan, /report

User Query: {user_message}
"""

            # Use AI to generate intelligent response with command routing
            response = await self._generate_ai_response_with_commands(user_message, context_info, portfolio, watchlist, signals)

            # Store bot response in memory
            try:
                await self._store_response_memory(user_id, username, response)
            except Exception as e:
                logger.warning(f"Response memory storage error: {e}")

            await update.message.reply_text(response, parse_mode='Markdown', disable_web_page_preview=True)

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

    async def _generate_ai_response_with_commands(self, query: str, context: str, portfolio: dict, watchlist: list, signals: list) -> str:
        """Generate intelligent AI response that can execute commands based on user intent"""
        try:
            # Try using Anthropic Claude API directly
            anthropic_key = os.getenv("ANTHROPIC_API_KEY")

            if anthropic_key:
                try:
                    import anthropic

                    client = anthropic.Anthropic(api_key=anthropic_key)

                    prompt = f"""You are AURA, an autonomous crypto trading intelligence assistant integrated with a Telegram bot.

{context}

Analyze the user's query and provide a helpful, data-rich response. You have access to real-time data:
- Portfolio data: {portfolio}
- Watchlist: {len(watchlist)} tokens
- Recent signals: {len(signals)} signals

If the user asks about:
- Portfolio/P&L → Show detailed portfolio stats with positions
- Signals → List recent signals with momentum scores and ages
- Watchlist → Show tracked tokens with Dexscreener links
- Tokens → Provide analysis and recommendations
- System status → Show scanner status and metrics

Format response in Markdown. Be concise but informative (3-5 sentences). Include relevant emojis.

User Query: {query}

Provide a complete, actionable response with real data."""

                    message = client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=500,
                        temperature=0.7,
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    )

                    ai_response = message.content[0].text
                    logger.info(f"✅ Claude API response: {ai_response[:50]}...")

                    return ai_response

                except ImportError:
                    logger.warning("anthropic package not installed, using fallback")
                except Exception as e:
                    logger.error(f"Claude API error: {e}")

            # Fallback: Smart contextual response with command execution
            query_lower = query.lower()

            if "portfolio" in query_lower or "pnl" in query_lower or "position" in query_lower:
                response = f"💼 *Portfolio Summary*\n\n"
                response += f"• Open Positions: {portfolio['open_positions']}\n"
                response += f"• Portfolio Value: ${portfolio['open_value_usd']:,.2f}\n"
                response += f"• Total P&L: ${portfolio['total_pnl_usd']:,.2f} ({portfolio['total_pnl_percent']:+.2f}%)\n"
                response += f"• Win Rate: {portfolio['win_rate']:.1f}%\n\n"
                response += f"Use /portfolio for full details"

            elif "signal" in query_lower:
                response = f"📡 *Recent Signals* (last 24h)\n\n"
                if signals:
                    for sig in signals[:5]:
                        symbol = sig.get('symbol', 'Unknown')
                        momentum = sig.get('momentum_score', 0)
                        address = sig.get('token_address', '')
                        response += f"• [{symbol}](https://dexscreener.com/solana/{address}) - Momentum: {momentum:.1f}\n"
                    response += f"\n{len(signals)} total signals"
                else:
                    response += "No signals in last 24h"
                response += f"\n\nUse /signals for more"

            elif "watchlist" in query_lower or "watch" in query_lower:
                response = f"👀 *Watchlist* ({len(watchlist)} tokens)\n\n"
                if watchlist:
                    for item in watchlist[:5]:
                        symbol = item.get('symbol', 'Unknown')
                        address = item.get('token_address', '')
                        response += f"• [{symbol}](https://dexscreener.com/solana/{address})\n"
                    response += f"\nUse /watchlist for full list"
                else:
                    response += "Watchlist is empty"

            elif "scan" in query_lower or "search" in query_lower or "find" in query_lower:
                response = f"🔍 *Scanner Status*\n\n"
                response += f"• Recent Signals: {len(signals)}\n"
                response += f"• Watchlist: {len(watchlist)} tokens\n\n"
                response += "Use /scan to trigger manual scan"

            else:
                response = f"🤖 *AURA Intelligence*\n\n"
                response += f"I can help you with:\n\n"
                response += f"💼 Portfolio: {portfolio['open_positions']} positions, ${portfolio['total_pnl_usd']:,.2f} P&L\n"
                response += f"📡 Signals: {len(signals)} in last 24h\n"
                response += f"👀 Watchlist: {len(watchlist)} tokens\n\n"
                response += f"Ask me about portfolio, signals, watchlist, or use /help"

            return response

        except Exception as e:
            logger.error(f"AI response generation error: {e}")
            return f"🤔 Processing your query: _{query}_\n\nUse /help for available commands."

    async def _generate_ai_response(self, query: str, context: str) -> str:
        """Legacy method - redirects to new command-aware version"""
        db = get_db()
        portfolio = db.get_portfolio_summary()
        watchlist = db.get_watchlist()
        signals = db.get_recent_helix_signals(hours=24, limit=5)
        return await self._generate_ai_response_with_commands(query, context, portfolio, watchlist, signals)

    async def _store_conversation_memory(self, user_id: int, username: str, message: str, portfolio: dict, signals: list, watchlist: list):
        """Store conversation in memory using database for persistence"""
        try:
            db = get_db()
            timestamp = datetime.now().isoformat()

            # Store in simple conversation log table
            with db._get_conn() as conn:
                cur = conn.cursor()

                # Create conversation_log table if it doesn't exist
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS conversation_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        username TEXT,
                        message TEXT,
                        message_type TEXT,
                        portfolio_summary TEXT,
                        signals_count INTEGER,
                        watchlist_count INTEGER,
                        timestamp TEXT
                    )
                """)

                # Insert conversation
                cur.execute("""
                    INSERT INTO conversation_log (user_id, username, message, message_type, portfolio_summary, signals_count, watchlist_count, timestamp)
                    VALUES (?, ?, ?, 'user', ?, ?, ?, ?)
                """, (
                    user_id,
                    username,
                    message,
                    f"{portfolio['open_positions']} positions, ${portfolio['total_pnl_usd']:.2f} P&L",
                    len(signals),
                    len(watchlist),
                    timestamp
                ))

                conn.commit()
                logger.info(f"✅ Stored conversation memory for {username}")

        except Exception as e:
            logger.error(f"Memory storage error: {e}")

    async def _store_response_memory(self, user_id: int, username: str, response: str):
        """Store bot response in memory"""
        try:
            db = get_db()
            timestamp = datetime.now().isoformat()

            with db._get_conn() as conn:
                cur = conn.cursor()

                cur.execute("""
                    INSERT INTO conversation_log (user_id, username, message, message_type, timestamp)
                    VALUES (?, ?, ?, 'bot', ?)
                """, (user_id, username, response, timestamp))

                conn.commit()

        except Exception as e:
            logger.error(f"Response memory storage error: {e}")


# Singleton
telegram_bot = AuraTelegramBot()
