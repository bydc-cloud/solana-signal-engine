#!/usr/bin/env python3
"""
AURA Background Worker
Runs autonomous actions: monitors signals, enriches tokens, executes strategies
"""
import time
import logging
from datetime import datetime

from aura.autonomous import autonomous_engine
from aura.mcps.crypto_mcp import crypto_mcp

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main worker loop"""
    logger.info("🤖 AURA Autonomous Worker starting...")

    cycle_count = 0

    while True:
        try:
            cycle_count += 1
            logger.info(f"🔄 AURA Worker Cycle #{cycle_count} - {datetime.now().isoformat()}")

            # Process new Helix signals
            processed = autonomous_engine.process_new_signals()
            if processed > 0:
                logger.info(f"✅ Processed {processed} new signals")

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
