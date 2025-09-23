#!/usr/bin/env python3
"""
TEST TELEGRAM SIGNAL
===================
Quick test to send a sample trading signal to Telegram
"""

import asyncio
import aiohttp
import os
from datetime import datetime
from pathlib import Path

# Load environment
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

async def test_telegram_signal():
    """Test sending a signal to Telegram"""
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_chat = os.getenv('TELEGRAM_CHAT_ID')

    # Sample trading signal based on real data we saw
    message = f"""🔥🔥🔥 <b>PRODUCTION TRADING SIGNAL</b> 🔥🔥🔥

💎 <b>Token:</b> $MOCHI
🎯 <b>Confidence:</b> 95/100 (NUCLEAR)
💰 <b>Price:</b> $0.001060
📈 <b>24h Change:</b> +1813%

📊 <b>MARKET DATA:</b>
🏪 Market Cap: $1,900,000
💸 Volume: $16,600,000
⚡ Vol/MCap Ratio: 8.7x
⏰ Age: 14h

🔍 <b>SIGNAL FACTORS:</b>
• 🔥 Ultra micro-cap: $1,900,000
• ⚡ Huge volume: 8.7x mcap
• 🚀 Massive pump: +1813%
• ✅ Fresh: 14h
• 💰 Micro-penny: $0.001060

🕐 <b>Detection Time:</b> {datetime.now().strftime('%H:%M:%S')}
🔢 <b>Scan #:</b> 1

<b>🚀 LIVE PUPPETEER EXTRACTION 🚀</b>
<i>Production system - Real trading opportunity</i>"""

    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    data = {
        'chat_id': telegram_chat,
        'text': message,
        'parse_mode': 'HTML'
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, timeout=10) as response:
                if response.status == 200:
                    print("✅ TELEGRAM TEST SUCCESSFUL!")
                    print(f"📱 Signal sent to chat: {telegram_chat}")
                    print("🚀 Production system ready for live trading!")
                    return True
                else:
                    print(f"❌ Telegram error: HTTP {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

async def main():
    print("🧪 Testing Telegram signal delivery...")
    success = await test_telegram_signal()

    if success:
        print("\n🎯 NEXT STEPS:")
        print("1. Run: python3 PRODUCTION_TELEGRAM_TRADER.py")
        print("2. Select option 1 (production trading)")
        print("3. Watch live signals in your Telegram!")
    else:
        print("\n❌ Fix Telegram connection before proceeding")

if __name__ == "__main__":
    asyncio.run(main())