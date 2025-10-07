#!/usr/bin/env python3
"""
UNIFIED SCANNER - AURA v0.3.0
Connects REALITY_MOMENTUM_SCANNER with IntelligentScanner
Generates signals using both rule-based and MCP-powered intelligence
"""
import asyncio
import logging
import os
from datetime import datetime
from typing import List, Dict

# Import existing scanners
from REALITY_MOMENTUM_SCANNER import RealityMomentumScanner
from aura.intelligent_scanner import intelligent_scanner
from aura.database import db
from aura.telegram_bot import telegram_bot

logger = logging.getLogger(__name__)

class UnifiedScanner:
    """
    Unified scanner combining rule-based and intelligent scanning
    """

    def __init__(self):
        self.reality_scanner = RealityMomentumScanner()
        self.intelligent_scanner = intelligent_scanner
        self.telegram_bot = telegram_bot
        self.last_intelligent_scan = None

        logger.info("🤖 UNIFIED SCANNER INITIALIZED")
        logger.info("  ⚡ Reality Momentum Scanner: Active")
        logger.info("  🧠 Intelligent Scanner (MCP): Active")
        logger.info("  📡 Telegram Bot: Active")

    async def run_combined_scan(self):
        """
        Run both scanners in parallel and combine results
        """
        logger.info("=" * 60)
        logger.info("🔍 COMBINED SCAN STARTING")
        logger.info("=" * 60)

        # Run both scanners in parallel
        reality_task = asyncio.create_task(self.run_reality_scan())
        intelligent_task = asyncio.create_task(self.run_intelligent_scan())

        # Wait for both to complete
        reality_signals, intelligent_signals = await asyncio.gather(
            reality_task,
            intelligent_task,
            return_exceptions=True
        )

        # Handle errors
        if isinstance(reality_signals, Exception):
            logger.error(f"Reality scanner error: {reality_signals}")
            reality_signals = 0

        if isinstance(intelligent_signals, Exception):
            logger.error(f"Intelligent scanner error: {intelligent_signals}")
            intelligent_signals = []

        logger.info("=" * 60)
        logger.info(f"✅ SCAN COMPLETE")
        logger.info(f"  ⚡ Reality signals sent: {reality_signals}")
        logger.info(f"  🧠 Intelligent signals stored: {len(intelligent_signals)}")
        logger.info("=" * 60)

        return {
            'reality_signals': reality_signals,
            'intelligent_signals': len(intelligent_signals),
            'timestamp': datetime.now().isoformat()
        }

    async def run_reality_scan(self):
        """
        Run the Reality Momentum Scanner (rule-based)
        """
        try:
            logger.info("⚡ Starting Reality Momentum Scanner...")
            signals_sent = await self.reality_scanner.run_scan_cycle()
            logger.info(f"⚡ Reality scanner sent {signals_sent} signals")
            return signals_sent
        except Exception as e:
            logger.error(f"Reality scanner error: {e}")
            return 0

    async def run_intelligent_scan(self):
        """
        Run the Intelligent Scanner (MCP-powered)
        """
        try:
            logger.info("🧠 Starting Intelligent Scanner (MCP)...")
            signals = await self.intelligent_scanner.scan_with_intelligence()

            # Send top intelligent signals to Telegram
            if signals:
                await self.send_intelligent_signals(signals[:5])  # Top 5

            logger.info(f"🧠 Intelligent scanner generated {len(signals)} signals")
            return signals
        except Exception as e:
            logger.error(f"Intelligent scanner error: {e}")
            return []

    async def send_intelligent_signals(self, signals: List[Dict]):
        """
        Send intelligent signals to Telegram
        """
        for signal in signals:
            try:
                message = self.format_intelligent_signal(signal)
                await self.telegram_bot.send_message(message)
                await asyncio.sleep(2)  # Rate limit
            except Exception as e:
                logger.error(f"Failed to send intelligent signal: {e}")

    def format_intelligent_signal(self, signal: Dict) -> str:
        """
        Format intelligent signal for Telegram
        """
        symbol = signal.get('symbol', 'UNKNOWN')
        momentum = signal.get('momentum_score', 0)
        sources = signal.get('sources', [])
        address = signal.get('address', '')

        source_str = ', '.join(sources)

        message = f"""🧠 <b>INTELLIGENT SIGNAL</b>

💎 <b>Token:</b> ${symbol}
📊 <b>Momentum Score:</b> {momentum:.1f}/100
🔍 <b>Sources:</b> {source_str}
🧾 <b>Address:</b> <code>{address}</code>

🔗 <a href="https://dexscreener.com/solana/{address}">DexScreener</a>

<b>🤖 AURA INTELLIGENT SCANNER</b>
<i>MCP-powered signal generation</i>"""

        return message

    async def run_continuous(self):
        """
        Run continuous unified scanning
        """
        logger.info("🚀 STARTING UNIFIED CONTINUOUS SCANNER")
        logger.info("  ⏱️  Reality Scan: Every 2 minutes")
        logger.info("  ⏱️  Intelligent Scan: Every 5 minutes")

        reality_interval = 120  # 2 minutes
        intelligent_interval = 300  # 5 minutes

        reality_last_run = 0
        intelligent_last_run = 0

        while True:
            try:
                current_time = asyncio.get_event_loop().time()

                tasks = []

                # Check if Reality scan needed
                if current_time - reality_last_run >= reality_interval:
                    logger.info("⚡ Triggering Reality scan...")
                    tasks.append(self.run_reality_scan())
                    reality_last_run = current_time

                # Check if Intelligent scan needed
                if current_time - intelligent_last_run >= intelligent_interval:
                    logger.info("🧠 Triggering Intelligent scan...")
                    tasks.append(self.run_intelligent_scan())
                    intelligent_last_run = current_time

                # Run tasks in parallel
                if tasks:
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    for result in results:
                        if isinstance(result, Exception):
                            logger.error(f"Scan error: {result}")

                # Sleep for 30 seconds before checking again
                await asyncio.sleep(30)

            except KeyboardInterrupt:
                logger.info("🛑 Scanner stopped by user")
                break
            except Exception as e:
                logger.error(f"Unified scanner error: {e}")
                await asyncio.sleep(60)  # Wait before retrying


async def main():
    """
    Main entry point
    """
    scanner = UnifiedScanner()
    await scanner.run_continuous()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    asyncio.run(main())
