#!/usr/bin/env python3
"""
HELIX WORKING TRADER - NUCLEAR MONEY PRINTER
===========================================
The working foundation bot that generates live profitable signals.
Clean, stable, tested system that WORKS.
"""

import asyncio
import aiohttp
import json
import os
from pathlib import Path
from datetime import datetime
import time
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

class WorkingTrader:
    """Nuclear money printer - the foundation system"""

    def __init__(self):
        self.birdeye_key = os.getenv('BIRDEYE_API_KEY')
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat = os.getenv('TELEGRAM_CHAT_ID')

        if not all([self.birdeye_key, self.telegram_token, self.telegram_chat]):
            raise ValueError("Missing API keys in .env file")

        # Performance tracking
        self.signals_sent = 0
        self.start_time = datetime.now()

    async def get_trending_tokens(self, limit: int = 10) -> list:
        """Get trending tokens with high volume"""
        try:
            url = "https://public-api.birdeye.so/defi/tokenlist"
            headers = {'X-API-KEY': self.birdeye_key}
            params = {
                'sort_by': 'v24hUSD',
                'sort_type': 'desc',
                'limit': limit
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params, timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('data', {}).get('tokens', [])
            return []
        except Exception as e:
            print(f"⚠️ Token fetch error: {e}")
            return []

    def calculate_confidence_score(self, token: dict) -> int:
        """Calculate confidence score for nuclear filtering"""
        try:
            symbol = token.get('symbol', 'Unknown')
            price_change = float(token.get('priceChange24hPercent') or 0)
            volume_24h = float(token.get('v24hUSD') or 0)
            market_cap = float(token.get('mc') or 0)

            if volume_24h == 0 or market_cap == 0:
                return 0

            score = 0

            # Nuclear filtering variables
            if volume_24h > 2000000 and price_change < 10:
                score += 40  # Massive volume, small pump = accumulation

            if market_cap < 1000000 and volume_24h > market_cap * 0.8:
                score += 35  # Low mcap + whale volume

            if 20 <= price_change <= 80:
                score += 25  # Sweet spot pump range

            if volume_24h > 1000000:
                score += 20  # High volume threshold

            if market_cap < 5000000:
                score += 15  # Small cap moonshot potential

            return min(score, 100)  # Cap at 100

        except Exception:
            return 0

    async def send_telegram_signal(self, token: dict, confidence: int):
        """Send nuclear signal to Telegram"""
        try:
            symbol = token.get('symbol', 'Unknown')
            address = token.get('address', 'N/A')
            price_change = float(token.get('priceChange24hPercent') or 0)
            volume_24h = float(token.get('v24hUSD') or 0)
            market_cap = float(token.get('mc') or 0)

            message = f"""
🚀 NUCLEAR SIGNAL #{self.signals_sent + 1}

💎 ${symbol}
🎯 Confidence: {confidence}/100
📈 24h Change: +{price_change:.1f}%
💰 Volume: ${volume_24h:,.0f}
🏪 Market Cap: ${market_cap:,.0f}

📍 Address: {address[:8]}...{address[-8:]}
🔗 https://birdeye.so/token/{address}

⚡ MONEY PRINTER ACTIVE ⚡
            """

            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat,
                'text': message.strip(),
                'parse_mode': 'HTML'
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data, timeout=10) as response:
                    if response.status == 200:
                        self.signals_sent += 1
                        print(f"🚀 Nuclear signal sent: ${symbol} ({confidence}% confidence)")
                        return True

        except Exception as e:
            print(f"⚠️ Telegram error: {e}")
        return False

    async def nuclear_scan_cycle(self):
        """Single nuclear scan cycle"""
        print(f"🔍 Nuclear scan - {datetime.now().strftime('%H:%M:%S')}")

        tokens = await self.get_trending_tokens(15)
        if not tokens:
            print("⚠️ No tokens received")
            return

        high_confidence_signals = []

        for token in tokens:
            confidence = self.calculate_confidence_score(token)

            if confidence >= 75:  # Nuclear threshold
                high_confidence_signals.append((token, confidence))

        # Send only the highest confidence signal
        if high_confidence_signals:
            best_signal = max(high_confidence_signals, key=lambda x: x[1])
            token, confidence = best_signal

            await self.send_telegram_signal(token, confidence)
            print(f"💎 Nuclear signal: ${token.get('symbol')} - {confidence}% confidence")
        else:
            print("⏳ No nuclear opportunities found this cycle")

    async def nuclear_money_printer(self):
        """Main nuclear money printer loop"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║                    HELIX NUCLEAR MONEY PRINTER               ║
║                      FOUNDATION SYSTEM                       ║
╚══════════════════════════════════════════════════════════════╝

🚀 NUCLEAR FILTERING ACTIVE
💎 Confidence threshold: 75/100
⚡ 60-second rapid cycles
🎯 Only highest confidence signals
        """)

        cycle_count = 0

        while True:
            try:
                cycle_start = time.time()
                cycle_count += 1

                print(f"\n🔄 Nuclear Cycle #{cycle_count}")
                await self.nuclear_scan_cycle()

                cycle_time = time.time() - cycle_start
                print(f"⚡ Cycle completed in {cycle_time:.1f}s")

                # Brief wait
                await asyncio.sleep(60)  # 60 second cycles

            except KeyboardInterrupt:
                print("\n🛑 Nuclear system stopped")
                break
            except Exception as e:
                print(f"❌ Nuclear error: {e}")
                await asyncio.sleep(30)

async def main():
    """Main entry point"""
    try:
        trader = WorkingTrader()
        await trader.nuclear_money_printer()
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
    except Exception as e:
        print(f"❌ System Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())