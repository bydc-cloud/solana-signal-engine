#!/usr/bin/env python3
"""
TEST FINAL DIRECT LINKS
======================
Final test with the updated direct link format
"""

import asyncio
import aiohttp
import os
from datetime import datetime
from pathlib import Path
import requests

# Load environment
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

async def test_final_direct_links():
    """Test the final direct link implementation"""
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_chat = os.getenv('TELEGRAM_CHAT_ID')
    birdeye_key = os.getenv('BIRDEYE_API_KEY')

    # Get a real token with real address
    try:
        url = "https://public-api.birdeye.so/defi/tokenlist"
        headers = {'X-API-KEY': birdeye_key}
        params = {'sort_by': 'v24hUSD', 'sort_type': 'desc', 'limit': 10}

        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            tokens = data.get('data', {}).get('tokens', [])

            # Use second token (first is usually SOL)
            real_token = tokens[1] if len(tokens) > 1 else tokens[0]
            symbol = real_token.get('symbol')
            address = real_token.get('address')

            # Generate DIRECT links (same as updated production code)
            coin_link = f'https://jup.ag/swap/SOL-{address}'  # Direct Jupiter
            chart_link = f'https://solscan.io/token/{address}'  # Direct Solscan
            info_link = f'https://birdeye.so/token/{address}'  # Direct Birdeye

            message = f"""🎯 <b>FINAL DIRECT LINK TEST</b> 🎯

💎 <b>Token:</b> <a href="{coin_link}">${symbol}</a> ← CLICK ME!

📱 <b>DIRECT LINKS (NO WRAPPER):</b>
• <a href="{coin_link}">🔄 Trade on Jupiter</a>
• <a href="{chart_link}">📊 View on Solscan</a>
• <a href="{info_link}">🔍 Info on Birdeye</a>

🔗 <b>Real Token Data:</b>
Symbol: {symbol}
Address: {address}
Price: ${real_token.get('price', 0):.8f}
Volume: ${real_token.get('v24hUSD', 0):,.0f}

💡 <b>These are DIRECT links:</b>
• No Phantom wrapper
• No universal link scheme
• Should open apps directly or in browser
• Real contract address used

🔗 <b>Raw URLs for verification:</b>
Jupiter: {coin_link}
Solscan: {chart_link}
Birdeye: {info_link}

🕐 <b>Test Time:</b> {datetime.now().strftime('%H:%M:%S')}

<b>✅ DIRECT LINK IMPLEMENTATION TEST ✅</b>"""

            url_tg = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
            data_tg = {
                'chat_id': telegram_chat,
                'text': message,
                'parse_mode': 'HTML'
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url_tg, data=data_tg, timeout=10) as response:
                    if response.status == 200:
                        print("✅ FINAL DIRECT LINK TEST SENT!")
                        print(f"📱 Token: ${symbol}")
                        print(f"🔗 Direct Jupiter: {coin_link}")
                        print(f"📊 Direct Solscan: {chart_link}")
                        print(f"🔍 Direct Birdeye: {info_link}")
                        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def main():
    print("🎯 Testing FINAL direct link implementation...")
    success = await test_final_direct_links()

    if success:
        print(f"\n✅ DIRECT LINKS DEPLOYED!")
        print("📱 These are the EXACT links production system will use")
        print("🎯 Test and report which format works best")
        print("🚀 System updated to use direct links (no wrappers)")

if __name__ == "__main__":
    asyncio.run(main())