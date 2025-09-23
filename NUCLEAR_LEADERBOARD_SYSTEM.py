#!/usr/bin/env python3
"""
NUCLEAR LEADERBOARD SYSTEM
==========================
Community-driven performance tracking and leaderboards for discovered gems.
Tracks 7d/30d performance with real-time gain/loss calculations.
"""

import asyncio
import json
import time
import os
import requests
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import aiohttp

# Load environment
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

class NuclearLeaderboardSystem:
    """Community leaderboard system for tracking gem performance"""

    def __init__(self):
        self.db_path = Path(__file__).parent / "nuclear_leaderboard.db"
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat = os.getenv('TELEGRAM_CHAT_ID')
        self.birdeye_key = os.getenv('BIRDEYE_API_KEY')

        # Initialize database
        self.init_database()

        print("""
╔══════════════════════════════════════════════════════════════╗
║         NUCLEAR LEADERBOARD SYSTEM ACTIVE                   ║
║           Community Performance Tracking                    ║
╚══════════════════════════════════════════════════════════════╝

📊 7d/30d Performance Leaderboards
🎯 Real-time Gain/Loss Tracking
💎 Community-Driven Discovery Validation
⚡ Live Performance Analytics
        """)

    def init_database(self):
        """Initialize SQLite database for tracking discoveries"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Table for discovered tokens
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS discovered_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                address TEXT UNIQUE NOT NULL,
                discovery_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                discovery_price REAL,
                discovery_mcap REAL,
                discovery_volume REAL,
                social_score INTEGER,
                source TEXT,
                is_active BOOLEAN DEFAULT 1
            )
            ''')

            # Table for price history
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_address TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                price REAL,
                mcap REAL,
                volume REAL,
                change_1h REAL,
                change_24h REAL,
                FOREIGN KEY (token_address) REFERENCES discovered_tokens (address)
            )
            ''')

            # Table for leaderboard entries
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS leaderboard_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_address TEXT NOT NULL,
                period_type TEXT NOT NULL, -- '7d' or '30d'
                start_price REAL,
                current_price REAL,
                performance_percent REAL,
                rank_position INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (token_address) REFERENCES discovered_tokens (address)
            )
            ''')

            conn.commit()
            print("✅ Nuclear Leaderboard database initialized")

    def add_discovered_token(self, token_data: dict, social_score: int):
        """Add a newly discovered token to tracking"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                symbol = token_data.get('symbol', 'UNKNOWN')
                address = token_data.get('address', '')
                price = self.parse_price(token_data.get('price', '$0'))
                mcap = self.parse_number(token_data.get('market_cap', '$0'))
                volume = self.parse_number(token_data.get('volume', '$0'))

                cursor.execute('''
                INSERT OR REPLACE INTO discovered_tokens
                (symbol, address, discovery_price, discovery_mcap, discovery_volume, social_score, source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (symbol, address, price, mcap, volume, social_score, 'nuclear_engine'))

                conn.commit()
                print(f"💎 DISCOVERY TRACKED: ${symbol} at ${price:.8f}")
                return True

        except Exception as e:
            print(f"⚠️ Discovery tracking error: {e}")
            return False

    def update_token_prices(self):
        """Update current prices for all tracked tokens"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Get all active tracked tokens
                cursor.execute('SELECT address FROM discovered_tokens WHERE is_active = 1')
                addresses = [row[0] for row in cursor.fetchall()]

                if not addresses:
                    print("📊 No tokens to update")
                    return

                print(f"🔄 Updating prices for {len(addresses)} tracked tokens...")

                # Update prices via Birdeye API
                if self.birdeye_key:
                    for address in addresses:
                        try:
                            url = f"https://public-api.birdeye.so/defi/price?address={address}"
                            headers = {'X-API-KEY': self.birdeye_key}

                            response = requests.get(url, headers=headers, timeout=5)
                            if response.status_code == 200:
                                data = response.json()
                                price_data = data.get('data', {})

                                if price_data:
                                    cursor.execute('''
                                    INSERT INTO price_history
                                    (token_address, price, mcap, volume, change_24h)
                                    VALUES (?, ?, ?, ?, ?)
                                    ''', (
                                        address,
                                        price_data.get('value', 0),
                                        price_data.get('mc', 0),
                                        price_data.get('v24hUSD', 0),
                                        price_data.get('priceChange24hPercent', 0)
                                    ))

                            time.sleep(0.2)  # Rate limiting

                        except Exception as e:
                            print(f"⚠️ Price update error for {address}: {e}")
                            continue

                conn.commit()
                print("✅ Price updates completed")

        except Exception as e:
            print(f"❌ Price update error: {e}")

    def calculate_leaderboards(self):
        """Calculate 7d and 30d performance leaderboards"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                periods = [
                    ('7d', 7),
                    ('30d', 30)
                ]

                for period_name, days in periods:
                    print(f"📊 Calculating {period_name} leaderboard...")

                    # Get tokens discovered within the period
                    cutoff_date = datetime.now() - timedelta(days=days)

                    cursor.execute('''
                    SELECT
                        dt.address,
                        dt.symbol,
                        dt.discovery_price,
                        dt.discovery_time,
                        (SELECT price FROM price_history
                         WHERE token_address = dt.address
                         ORDER BY timestamp DESC LIMIT 1) as current_price
                    FROM discovered_tokens dt
                    WHERE dt.discovery_time >= ? AND dt.is_active = 1
                    ''', (cutoff_date,))

                    results = cursor.fetchall()

                    leaderboard = []
                    for address, symbol, discovery_price, discovery_time, current_price in results:
                        if discovery_price and current_price and discovery_price > 0:
                            performance = ((current_price - discovery_price) / discovery_price) * 100
                            leaderboard.append({
                                'address': address,
                                'symbol': symbol,
                                'discovery_price': discovery_price,
                                'current_price': current_price,
                                'performance': performance,
                                'discovery_time': discovery_time
                            })

                    # Sort by performance
                    leaderboard.sort(key=lambda x: x['performance'], reverse=True)

                    # Update leaderboard entries
                    cursor.execute('DELETE FROM leaderboard_entries WHERE period_type = ?', (period_name,))

                    for rank, entry in enumerate(leaderboard, 1):
                        cursor.execute('''
                        INSERT INTO leaderboard_entries
                        (token_address, period_type, start_price, current_price, performance_percent, rank_position)
                        VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            entry['address'],
                            period_name,
                            entry['discovery_price'],
                            entry['current_price'],
                            entry['performance'],
                            rank
                        ))

                    print(f"✅ {period_name} leaderboard: {len(leaderboard)} entries")

                conn.commit()

        except Exception as e:
            print(f"❌ Leaderboard calculation error: {e}")

    def get_leaderboard(self, period: str = '7d', limit: int = 10) -> list:
        """Get current leaderboard for specified period"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                SELECT
                    dt.symbol,
                    le.start_price,
                    le.current_price,
                    le.performance_percent,
                    le.rank_position,
                    dt.discovery_time
                FROM leaderboard_entries le
                JOIN discovered_tokens dt ON le.token_address = dt.address
                WHERE le.period_type = ?
                ORDER BY le.rank_position
                LIMIT ?
                ''', (period, limit))

                results = cursor.fetchall()

                leaderboard = []
                for symbol, start_price, current_price, performance, rank, discovery_time in results:
                    leaderboard.append({
                        'rank': rank,
                        'symbol': symbol,
                        'start_price': start_price,
                        'current_price': current_price,
                        'performance': performance,
                        'discovery_time': discovery_time
                    })

                return leaderboard

        except Exception as e:
            print(f"⚠️ Leaderboard retrieval error: {e}")
            return []

    async def send_leaderboard_update(self, period: str = '7d'):
        """Send leaderboard update to Telegram"""
        try:
            leaderboard = self.get_leaderboard(period, 10)

            if not leaderboard:
                print(f"📊 No {period} leaderboard data to send")
                return

            # Format leaderboard message
            period_emoji = "📅" if period == '7d' else "🗓️"
            title = f"{period_emoji} <b>NUCLEAR {period.upper()} LEADERBOARD</b> {period_emoji}"

            leaderboard_text = []
            for entry in leaderboard:
                rank_emoji = ["🥇", "🥈", "🥉"][entry['rank']-1] if entry['rank'] <= 3 else f"{entry['rank']}."

                performance_emoji = "🚀" if entry['performance'] > 100 else "📈" if entry['performance'] > 0 else "📉"

                leaderboard_text.append(
                    f"{rank_emoji} ${entry['symbol']}: {performance_emoji} {entry['performance']:+.1f}%"
                )

            message = f"""{title}

🏆 <b>TOP PERFORMING DISCOVERIES:</b>

{chr(10).join(leaderboard_text)}

⏰ <b>Period:</b> Last {period}
💎 <b>Discoveries Tracked:</b> {len(leaderboard)}
🎯 <b>Best Performance:</b> {leaderboard[0]['performance']:+.1f}%

<b>🚀 NUCLEAR LEADERBOARD SYSTEM 🚀</b>
<i>Community-driven performance tracking</i>"""

            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat,
                'text': message,
                'parse_mode': 'HTML'
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data, timeout=15) as response:
                    if response.status == 200:
                        print(f"📊 {period} leaderboard sent to Telegram")
                        return True
                    else:
                        print(f"❌ Telegram error: HTTP {response.status}")

        except Exception as e:
            print(f"⚠️ Leaderboard send error: {e}")

        return False

    def parse_price(self, price_str: str) -> float:
        """Parse price string to float"""
        try:
            return float(str(price_str).replace('$', '').replace(',', ''))
        except:
            return 0.0

    def parse_number(self, num_str: str) -> float:
        """Parse number with K/M/B suffixes"""
        try:
            if not num_str or num_str == 'N/A':
                return 0.0

            clean_str = str(num_str).replace('$', '').replace(',', '').upper()

            multiplier = 1
            if 'K' in clean_str:
                multiplier = 1000
                clean_str = clean_str.replace('K', '')
            elif 'M' in clean_str:
                multiplier = 1000000
                clean_str = clean_str.replace('M', '')
            elif 'B' in clean_str:
                multiplier = 1000000000
                clean_str = clean_str.replace('B', '')

            return float(clean_str) * multiplier
        except:
            return 0.0

    async def run_leaderboard_updates(self):
        """Run continuous leaderboard updates"""
        print("""
🚀 NUCLEAR LEADERBOARD UPDATES STARTING
═══════════════════════════════════════
• Price tracking every 10 minutes
• Leaderboard calculations every hour
• Telegram updates every 4 hours
        """)

        last_price_update = 0
        last_leaderboard_calc = 0
        last_telegram_update = 0

        try:
            while True:
                current_time = time.time()

                # Update prices every 10 minutes
                if current_time - last_price_update >= 600:
                    self.update_token_prices()
                    last_price_update = current_time

                # Calculate leaderboards every hour
                if current_time - last_leaderboard_calc >= 3600:
                    self.calculate_leaderboards()
                    last_leaderboard_calc = current_time

                # Send Telegram updates every 4 hours
                if current_time - last_telegram_update >= 14400:
                    await self.send_leaderboard_update('7d')
                    await asyncio.sleep(30)
                    await self.send_leaderboard_update('30d')
                    last_telegram_update = current_time

                await asyncio.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            print("🛑 Leaderboard system stopped")
        except Exception as e:
            print(f"❌ Leaderboard system error: {e}")

async def main():
    """Test leaderboard system"""
    try:
        leaderboard = NuclearLeaderboardSystem()

        # Add some test data
        test_tokens = [
            {'symbol': 'TESTGEM1', 'address': 'test1addr', 'price': '$0.001', 'market_cap': '$12000', 'volume': '$50000'},
            {'symbol': 'TESTGEM2', 'address': 'test2addr', 'price': '$0.05', 'market_cap': '$14500', 'volume': '$75000'},
        ]

        for token in test_tokens:
            leaderboard.add_discovered_token(token, 75)

        # Test leaderboard display
        print("\n🧪 Testing leaderboard retrieval...")
        board_7d = leaderboard.get_leaderboard('7d', 5)
        print(f"7d leaderboard: {len(board_7d)} entries")

        # Send test leaderboard
        await leaderboard.send_leaderboard_update('7d')

    except KeyboardInterrupt:
        print("\n🛑 Test stopped")
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    asyncio.run(main())