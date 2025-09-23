#!/usr/bin/env python3
"""
TEST CLICKABLE COIN LINK
=======================
Test the exact clickable $COIN functionality
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

async def test_clickable_coin_signal():
    """Test signal with clickable $COIN link"""
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_chat = os.getenv('TELEGRAM_CHAT_ID')

    # Real token data with actual address for testing
    symbol = 'MOCHI'
    token_address = 'EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm'

    # Generate the clickable link (DexScreener opens in iPhone trading apps)
    coin_link = f'https://dexscreener.com/solana/{token_address}'
    birdeye_link = f'https://birdeye.so/token/{token_address}'
    jupiter_link = f'https://jup.ag/swap/SOL-{token_address}'

    # Test signal with clickable $COIN
    message = f"""🔥🔥 <b>CLICKABLE COIN TEST SIGNAL</b> 🔥🔥

💎 <b>Token:</b> <a href="{coin_link}">${symbol}</a> ← CLICK THIS!
🎯 <b>Confidence:</b> 95/100 (NUCLEAR)
💰 <b>Price:</b> $0.001060
📈 <b>24h Change:</b> +1813%

📊 <b>MARKET DATA:</b>
🏪 Market Cap: $1,900,000
💸 Volume: $16,600,000
⚡ Vol/MCap Ratio: 8.7x

📱 <b>iPhone App Links (All Clickable):</b>
• <a href="{coin_link}">📊 View Chart (Opens Trading App)</a>
• <a href="{birdeye_link}">🔍 Token Info</a>
• <a href="{jupiter_link}">🔄 Buy on Jupiter</a>

🕐 <b>Test Time:</b> {datetime.now().strftime('%H:%M:%S')}

<b>✅ CLICKABLE $COIN LINK VERIFICATION ✅</b>
<i>Tap ${symbol} above - should open iPhone trading app!</i>"""

    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    data = {
        'chat_id': telegram_chat,
        'text': message,
        'parse_mode': 'HTML',
        'disable_web_page_preview': False  # Allow link preview
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, timeout=10) as response:
                if response.status == 200:
                    print("✅ CLICKABLE COIN LINK TEST SUCCESSFUL!")
                    print(f"📱 Check your Telegram chat: {telegram_chat}")
                    print(f"🎯 Tap '${symbol}' to verify it opens your iPhone trading app")
                    print(f"🔗 Link: {coin_link}")
                    return True
                else:
                    print(f"❌ Telegram error: HTTP {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

async def main():
    print("🧪 Testing clickable $COIN functionality...")
    print("📱 This will send a test signal with clickable coin link")

    success = await test_clickable_coin_signal()

    if success:
        print(f"\n✅ VERIFICATION COMPLETE!")
        print("📱 Check your Telegram - you should see:")
        print("   • Clickable '$MOCHI' that opens iPhone trading app")
        print("   • Three action buttons with direct app links")
        print("   • Proper HTML formatting with links")
        print(f"\n🚀 Production system ready with clickable coins!")
    else:
        print("\n❌ Test failed - check connection")

if __name__ == "__main__":
    asyncio.run(main())