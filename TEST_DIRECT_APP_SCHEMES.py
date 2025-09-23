#!/usr/bin/env python3
"""
TEST DIRECT APP SCHEMES
======================
Test direct mobile app schemes that bypass web pages
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

async def test_direct_app_schemes():
    """Test direct mobile app URL schemes"""
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_chat = os.getenv('TELEGRAM_CHAT_ID')

    # Use a real popular token address
    test_address = "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"  # BONK
    symbol = "BONK"

    # Direct app scheme URLs (no web wrappers)
    link1 = f"https://app.jup.ag/swap/SOL-{test_address}"  # Direct Jupiter web app
    link2 = f"https://solscan.io/token/{test_address}"  # Direct Solscan
    link3 = f"https://birdeye.so/token/{test_address}"  # Direct Birdeye
    link4 = f"https://raydium.io/swap/?inputCurrency=sol&outputCurrency={test_address}"  # Direct Raydium
    link5 = f"https://jup.ag/swap/SOL-{test_address}?referrer=4MangoMjqJ2firMokCjjGgoK8d4MXcrgL7XJaL3w6fVg"  # Jupiter with referrer

    message = f"""🧪 <b>DIRECT APP SCHEME TEST</b> 🧪

💎 <b>Token:</b> ${symbol}
🔗 <b>Address:</b> {test_address}

📱 <b>TEST THESE DIRECT LINKS:</b>

1. <a href="{link1}">Jupiter Direct: ${symbol}</a>
2. <a href="{link2}">Solscan Direct: ${symbol}</a>
3. <a href="{link3}">Birdeye Direct: ${symbol}</a>
4. <a href="{link4}">Raydium Direct: ${symbol}</a>
5. <a href="{link5}">Jupiter+Referrer: ${symbol}</a>

🎯 <b>TESTING INSTRUCTIONS:</b>
• These are DIRECT links (no Phantom wrapper)
• Should open apps directly or prompt app selection
• Tell me which ones actually work on mobile
• Which one opens the token correctly?

🔗 <b>Direct URLs:</b>
1. {link1}
2. {link2}
3. {link3}
4. {link4}
5. {link5}

🕐 <b>Test Time:</b> {datetime.now().strftime('%H:%M:%S')}

<b>🎯 FIND THE WORKING DIRECT LINK FORMAT 🎯</b>"""

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
                    print("✅ DIRECT APP SCHEME TESTS SENT!")
                    print(f"📱 Testing direct links without Phantom wrapper")
                    print(f"🎯 These should bypass homepage and go directly to token")
                    print("\n🔗 Direct Test Links:")
                    print(f"1. Jupiter: {link1}")
                    print(f"2. Solscan: {link2}")
                    print(f"3. Birdeye: {link3}")
                    print(f"4. Raydium: {link4}")
                    print(f"5. Jupiter+Ref: {link5}")
                    return True
                else:
                    print(f"❌ Telegram error: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def main():
    print("🧪 Testing DIRECT app schemes (no Phantom wrapper)...")
    success = await test_direct_app_schemes()

    if success:
        print(f"\n✅ DIRECT SCHEME TESTS DEPLOYED!")
        print("📱 Test each link on your iPhone")
        print("🎯 Find which one opens the token directly")
        print("🔧 Report back which format actually works")
        print("\n💡 These bypass Phantom wrapper completely")

if __name__ == "__main__":
    asyncio.run(main())