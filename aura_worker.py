#!/usr/bin/env python3
"""
AURA Background Worker
Runs autonomous actions: monitors signals, enriches tokens, executes strategies
"""
import time
import logging
import asyncio
from datetime import datetime

from aura.autonomous import autonomous_engine
from aura.mcps.crypto_mcp import crypto_mcp
from aura.governance import governance
from aura.sentiment import sentiment_analyzer
from aura.whale_tracker import whale_tracker

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def check_governance_proposals():
    """Check and finalize ended proposal voting periods"""
    try:
        proposals = governance.get_active_proposals()
        for proposal in proposals:
            # Check if voting period ended
            voting_ends = datetime.fromisoformat(proposal['voting_ends_at'])
            if datetime.now() > voting_ends:
                logger.info(f"Finalizing proposal {proposal['id']}: {proposal['title']}")
                governance.finalize_proposal(proposal['id'])

                # Auto-execute if passed
                results = governance.get_voting_results(proposal['id'])
                if results['results']['for']['power'] > results['results']['against']['power']:
                    logger.info(f"Executing passed proposal {proposal['id']}")
                    governance.execute_proposal(proposal['id'])

    except Exception as e:
        logger.error(f"Governance check error: {e}")


async def check_whale_activity():
    """Monitor whale wallets for copy trading signals"""
    try:
        signals = await whale_tracker.get_whale_copy_signals()
        if signals:
            logger.info(f"🐋 Found {len(signals)} whale copy trading signals")
            # TODO: Process whale signals through autonomous engine

    except Exception as e:
        logger.error(f"Whale tracking error: {e}")


async def analyze_sentiment():
    """Periodic sentiment analysis for watchlist tokens"""
    try:
        from aura.database import db
        watchlist = db.get_watchlist()

        if not watchlist:
            return

        # Analyze top 5 watchlist tokens
        for item in watchlist[:5]:
            address = item['token_address']
            symbol = item.get('symbol', '')

            sentiment = await sentiment_analyzer.analyze_token_sentiment(address, symbol)

            if sentiment['overall_score'] > 0:
                logger.info(f"📊 {symbol} sentiment: {sentiment['overall_score']} ({sentiment['total_mentions']} mentions)")

    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")


async def async_worker_cycle(cycle_count: int):
    """Async worker cycle with all background tasks"""
    logger.info(f"🔄 AURA Worker Cycle #{cycle_count} - {datetime.now().isoformat()}")

    # 1. Process new Helix signals (core function)
    processed = autonomous_engine.process_new_signals()
    if processed > 0:
        logger.info(f"✅ Processed {processed} new signals")

    # 2. Check governance proposals (every cycle)
    await check_governance_proposals()

    # 3. 🔧 MCP TOOL: Discover trending tokens (every 20 cycles = ~10 minutes)
    if cycle_count % 20 == 0:
        try:
            trending_count = autonomous_engine.discover_trending_tokens()
            if trending_count > 0:
                logger.info(f"🔥 MCP: Added {trending_count} trending tokens from CoinGecko")
        except Exception as e:
            logger.error(f"Trending discovery error: {e}")

    # 4. Check whale activity (every 5 cycles = ~2.5 minutes)
    if cycle_count % 5 == 0:
        await check_whale_activity()

    # 5. Analyze sentiment (every 10 cycles = ~5 minutes)
    if cycle_count % 10 == 0:
        await analyze_sentiment()


async def setup_telegram_bot():
    """Setup Telegram bot command handlers"""
    try:
        from aura.telegram_bot import telegram_bot

        if telegram_bot.enabled:
            await telegram_bot.setup_commands()
            logger.info("✅ Telegram bot command handlers setup complete")
    except Exception as e:
        logger.error(f"Telegram bot setup error: {e}")


def main():
    """Main worker loop"""
    logger.info("🤖 AURA Autonomous Worker starting...")
    logger.info("✨ Features: Signal Processing, Governance, Whale Tracking, Sentiment Analysis")
    logger.info("🔧 MCP Tools: CoinGecko, Firecrawl, Memory, Puppeteer, Context7")

    # Setup Telegram bot in background
    try:
        asyncio.run(setup_telegram_bot())
    except Exception as e:
        logger.warning(f"Telegram setup failed: {e}")

    cycle_count = 0

    while True:
        try:
            cycle_count += 1

            # Run async worker cycle
            asyncio.run(async_worker_cycle(cycle_count))

            # Sleep for 30 seconds
            time.sleep(30)

        except KeyboardInterrupt:
            logger.info("🛑 AURA Worker stopping...")
            break
        except Exception as e:
            logger.error(f"❌ AURA Worker error: {e}")
            time.sleep(10)  # Sleep on error


if __name__ == "__main__":
    main()
