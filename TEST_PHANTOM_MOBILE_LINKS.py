#!/usr/bin/env python3
"""
TEST PHANTOM MOBILE DEEP LINKS
==============================
Test multiple Phantom deep link formats to find the one that works on mobile
"""

import asyncio
import aiohttp
import os
from datetime import datetime
from pathlib import Path
import urllib.parse

# Load environment
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

async def test_phantom_mobile_links():
    """Test multiple Phantom deep link formats for mobile"""
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_chat = os.getenv('TELEGRAM_CHAT_ID')

    symbol = 'BONK'

    # Multiple deep link formats to test
    link1 = f'https://phantom.app/ul/browse/https%3A//jup.ag/swap/SOL-{symbol}'
    link2 = f'phantom://browse/https://jup.ag/swap/SOL-{symbol}'
    link3 = f'https://phantom.app/ul/v1/browse/https%3A//jup.ag/swap/SOL-{symbol}'
    link4 = f'phantom://swap/SOL/{symbol}'
    link5 = f'https://phantom.app/ul/browse/{urllib.parse.quote("https://jup.ag/swap/SOL-" + symbol, safe="")}'

    message = f"""🧪 <b>PHANTOM MOBILE DEEP LINK TEST</b> 🧪

💎 <b>Token:</b> ${symbol}

📱 <b>TEST THESE LINKS ON YOUR iPhone:</b>

1. <a href="{link1}">Universal Link v1: ${symbol}</a>
2. <a href="{link2}">Direct Phantom Scheme: ${symbol}</a>
3. <a href="{link3}">Universal Link v2: ${symbol}</a>
4. <a href="{link4}">Phantom Swap Direct: ${symbol}</a>
5. <a href="{link5}">Encoded Universal: ${symbol}</a>

🎯 <b>INSTRUCTIONS:</b>
• Tap each link above on your iPhone
• Tell me which one shows "Open in Phantom?" popup
• Or which one directly opens Phantom app

🔗 <b>Raw URLs for verification:</b>
Link 1: {link1}
Link 2: {link2}
Link 3: {link3}
Link 4: {link4}
Link 5: {link5}

🕐 <b>Test Time:</b> {datetime.now().strftime('%H:%M:%S')}

<b>⚡ FIND THE WORKING PHANTOM DEEP LINK ⚡</b>"""

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
                    print("✅ PHANTOM DEEP LINK TESTS SENT!")
                    print(f"📱 Check Telegram and test each link on iPhone")
                    print(f"🎯 Find which one triggers Phantom app opening")
                    print("\n🔗 Test Links:")
                    print(f"1. {link1}")
                    print(f"2. {link2}")
                    print(f"3. {link3}")
                    print(f"4. {link4}")
                    print(f"5. {link5}")
                    return True
                else:
                    print(f"❌ Telegram error: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def main():
    print("🧪 Testing multiple Phantom mobile deep link formats...")
    success = await test_phantom_mobile_links()

    if success:
        print(f"\n✅ PHANTOM DEEP LINK TESTS DEPLOYED!")
        print("📱 Test each link on your iPhone")
        print("🎯 Report back which one actually opens Phantom")
        print("🔧 I'll update the production system with the working format")

if __name__ == "__main__":
    asyncio.run(main())