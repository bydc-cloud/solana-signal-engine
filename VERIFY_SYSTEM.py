#!/usr/bin/env python3
"""
HELIX SYSTEM VERIFICATION
=========================
Verify all systems are working with real live signals
"""

import asyncio
import aiohttp
import json
import os
from pathlib import Path
from datetime import datetime
import random

# Load environment
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

class SystemVerification:
    """Verify all systems are working"""

    def __init__(self):
        self.birdeye_key = os.getenv('BIRDEYE_API_KEY')
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat = os.getenv('TELEGRAM_CHAT_ID')

    async def test_birdeye_api(self):
        """Test Birdeye API connection"""
        try:
            url = "https://public-api.birdeye.so/defi/tokenlist"
            headers = {'X-API-KEY': self.birdeye_key}
            params = {'sort_by': 'v24hUSD', 'sort_type': 'desc', 'limit': 5}

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        tokens = data.get('data', {}).get('tokens', [])
                        if tokens:
                            # Get random token for variety
                            token = random.choice(tokens)
                            symbol = token.get('symbol', 'Unknown')
                            volume = float(token.get('v24hUSD') or 0)
                            print(f"✅ Birdeye API: Live data - ${symbol} (${volume:,.0f} volume)")
                            return True, token
            return False, None
        except Exception as e:
            print(f"❌ Birdeye API Error: {e}")
            return False, None

    async def test_telegram_bot(self, test_token=None):
        """Test Telegram bot with live signal"""
        try:
            if test_token:
                symbol = test_token.get('symbol', 'TEST')
                price_change = float(test_token.get('priceChange24hPercent') or 0)
                volume = float(test_token.get('v24hUSD') or 0)
                market_cap = float(test_token.get('mc') or 0)

                message = f"""
🧪 SYSTEM VERIFICATION TEST

💎 Live Token: ${symbol}
📈 24h Change: +{price_change:.1f}%
💰 Volume: ${volume:,.0f}
🏪 Market Cap: ${market_cap:,.0f}

✅ All systems operational
🚀 Nuclear money printer ready
⚡ Time: {datetime.now().strftime('%H:%M:%S')}
                """
            else:
                message = "🧪 HELIX SYSTEM TEST - All systems operational! 🚀"

            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat,
                'text': message.strip()
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data, timeout=10) as response:
                    if response.status == 200:
                        print("✅ Telegram Bot: Message sent successfully")
                        return True

        except Exception as e:
            print(f"❌ Telegram Error: {e}")
        return False

    async def verify_all_systems(self):
        """Run complete system verification"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║                    HELIX SYSTEM VERIFICATION                 ║
║                      LIVE SYSTEM TEST                        ║
╚══════════════════════════════════════════════════════════════╝

🧪 Testing all nuclear money printer components...
        """)

        # Test Birdeye API
        print("1️⃣ Testing Birdeye API connection...")
        birdeye_success, test_token = await self.test_birdeye_api()

        # Test Telegram Bot
        print("2️⃣ Testing Telegram bot...")
        telegram_success = await self.test_telegram_bot(test_token)

        # Results
        print(f"""
📊 VERIFICATION RESULTS:
════════════════════════
✅ Birdeye API: {'WORKING' if birdeye_success else 'FAILED'}
✅ Telegram Bot: {'WORKING' if telegram_success else 'FAILED'}

🎯 System Status: {'🚀 READY FOR NUCLEAR TRADING' if all([birdeye_success, telegram_success]) else '❌ NEEDS ATTENTION'}
        """)

        if all([birdeye_success, telegram_success]):
            print("💎 All systems verified! Nuclear money printer is operational!")
            print("🚀 Run WORKING_TRADER.py to start making money")
            print("📊 Run DATA_COLLECTOR.py for intelligence gathering")
            print("🧠 Run INTELLIGENT_TRADER.py for nuclear filtering")
            return True
        else:
            print("❌ System verification failed. Check your API keys.")
            return False

async def main():
    """Main verification"""
    try:
        verifier = SystemVerification()
        await verifier.verify_all_systems()
    except Exception as e:
        print(f"❌ Verification Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())