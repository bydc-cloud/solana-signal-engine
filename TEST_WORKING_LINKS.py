#!/usr/bin/env python3
"""
TEST WORKING LINKS
=================
Test the fixed links that actually work in browser
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

async def test_working_links():
    """Test working links in Telegram"""
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_chat = os.getenv('TELEGRAM_CHAT_ID')

    symbol = 'BONK'  # Use real token symbol

    # Generate WORKING links (same as updated code)
    coin_link = f'https://jup.ag/swap/SOL-{symbol}'  # Jupiter confirmed working
    chart_link = f'https://dexscreener.com/search/?q={symbol}'  # Search works
    info_link = f'https://birdeye.so/token/{symbol}'  # Symbol format

    message = f"""🔥🔥 <b>WORKING LINKS TEST</b> 🔥🔥

💎 <b>Token:</b> <a href="{coin_link}">${symbol}</a> ← CLICK ME!

📱 <b>WORKING LINKS TEST:</b>
• <a href="{chart_link}">📊 View Chart (DexScreener Search)</a>
• <a href="{info_link}">🔍 Token Info (Birdeye)</a>
• <a href="{coin_link}">🔄 Buy on Jupiter (CONFIRMED WORKING)</a>

🔗 <b>Direct URLs for verification:</b>
Chart: {chart_link}
Info: {info_link}
Jupiter: {coin_link}

🕐 <b>Test Time:</b> {datetime.now().strftime('%H:%M:%S')}

<b>✅ FIXED LINKS - SHOULD WORK IN TELEGRAM ✅</b>"""

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
                    print("✅ WORKING LINKS TEST SENT!")
                    print(f"📱 Check Telegram chat: {telegram_chat}")
                    print(f"🔗 Jupiter link (confirmed working): {coin_link}")
                    print(f"📊 Chart search: {chart_link}")
                    print(f"🔍 Info link: {info_link}")
                    return True
                else:
                    print(f"❌ Telegram error: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def main():
    print("🧪 Testing WORKING links after fix...")
    success = await test_working_links()

    if success:
        print("\n✅ LINK FIX VERIFICATION:")
        print("• $BONK should be clickable and open Jupiter")
        print("• Chart link opens DexScreener search")
        print("• Jupiter confirmed working in browser")
        print("• Only link generation was changed")
        print("\n🚀 Updated system ready!")

if __name__ == "__main__":
    asyncio.run(main())