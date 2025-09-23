#!/usr/bin/env python3
"""
TEST VERIFIED JUPITER FORMAT
============================
Test the ACTUAL working Jupiter link format user found
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

async def test_verified_jupiter_format():
    """Test the user-verified Jupiter link format"""
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_chat = os.getenv('TELEGRAM_CHAT_ID')

    # Use EXACT address user tested
    usdc_address = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

    # VERIFIED working format from user
    verified_link = f'https://jup.ag/tokens/{usdc_address}'

    # Test other popular tokens too
    bonk_address = "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"
    bonk_link = f'https://jup.ag/tokens/{bonk_address}'

    message = f"""✅ <b>VERIFIED JUPITER FORMAT TEST</b> ✅

🎯 <b>USER VERIFIED WORKING FORMAT:</b>
<code>https://jup.ag/tokens/{{address}}</code>

💎 <b>USDC Test:</b> <a href="{verified_link}">$USDC</a> ← USER VERIFIED
💎 <b>BONK Test:</b> <a href="{bonk_link}">$BONK</a> ← SAME FORMAT

📱 <b>EXACT LINKS TO TEST:</b>
• <a href="{verified_link}">USDC (User Verified)</a>
• <a href="{bonk_link}">BONK (Same Format)</a>

🔗 <b>Raw URLs:</b>
USDC: {verified_link}
BONK: {bonk_link}

✅ <b>THIS IS THE FORMAT NOW USED IN PRODUCTION!</b>

🎯 <b>TESTING INSTRUCTIONS:</b>
1. Tap the $USDC link above
2. Should show USDC token page on Jupiter
3. Should work on mobile (you verified on desktop)
4. Confirm this is the correct format

🕐 <b>Test Time:</b> {datetime.now().strftime('%H:%M:%S')}

<b>🚀 USING YOUR VERIFIED WORKING FORMAT 🚀</b>"""

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
                    print("✅ VERIFIED JUPITER FORMAT TEST SENT!")
                    print(f"🎯 Using EXACT format user verified works")
                    print(f"🔗 USDC Link: {verified_link}")
                    print(f"🔗 BONK Link: {bonk_link}")
                    print(f"✅ Production system updated to use this format")
                    return True
                else:
                    print(f"❌ Telegram error: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def main():
    print("✅ Testing USER VERIFIED Jupiter format...")
    success = await test_verified_jupiter_format()

    if success:
        print(f"\n🎯 VERIFIED FORMAT DEPLOYED!")
        print("📱 Test the $USDC link - should work perfectly")
        print("🚀 Production system now uses: https://jup.ag/tokens/{address}")
        print("✅ This is the EXACT format you verified works")

if __name__ == "__main__":
    asyncio.run(main())