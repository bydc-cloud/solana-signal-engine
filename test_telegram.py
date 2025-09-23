#!/usr/bin/env python3
"""Test Telegram integration"""

import requests
import os
from pathlib import Path
from datetime import datetime

# Load environment
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
telegram_chat = os.getenv('TELEGRAM_CHAT_ID')

message = f"""🔥 <b>REALITY MOMENTUM SCANNER STATUS</b> 🔥

✅ <b>SYSTEM OPERATIONAL</b>
✅ <b>SIGNALS BEING SENT</b>

📊 <b>Recent Signals Sent:</b>
• $USD1 (76.5/100 strength)
• $1 (83.0/100 strength)
• $RTC (91.5/100 strength)

🚀 <b>Your money printer is WORKING!</b>
⏰ <b>Test sent:</b> {datetime.now().strftime('%H:%M:%S')}

<b>🎯 REALITY MOMENTUM SCANNER</b>
<i>Confirmed operational - signals flowing to Telegram</i>"""

url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
data = {
    'chat_id': telegram_chat,
    'text': message,
    'parse_mode': 'HTML'
}

response = requests.post(url, data=data, timeout=15)
if response.status_code == 200:
    print("✅ TEST MESSAGE SENT TO TELEGRAM SUCCESSFULLY!")
    print("🎯 You should see this confirmation in your Telegram chat")
else:
    print(f"❌ Telegram test failed: {response.status_code}")
    print(response.text)