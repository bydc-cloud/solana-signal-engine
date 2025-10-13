#!/usr/bin/env python3
"""
DEXSCREENER MOMENTUM SCANNER
============================
Fallback scanner using DexScreener API (no API key required)
Generates signals from Solana trending tokens
"""

import asyncio
import aiohttp
import logging
import os
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Scanner configuration
MIN_LIQUIDITY_USD = 5000      # Lowered from 10k
MIN_VOLUME_24H = 2000         # Lowered from 5k
MIN_MARKET_CAP = 20000        # Lowered from 30k
MAX_MARKET_CAP = 1000000      # Raised from 500k
MIN_PRICE_CHANGE_24H = 5      # Lowered from 10% to 5%
SCAN_INTERVAL_SECONDS = 120
DB_PATH = Path("data/final_nuclear.db")

class DexScreenerScanner:
    """
    Fallback scanner using free DexScreener API
    """

    def __init__(self):
        self.base_url = "https://api.dexscreener.com/latest/dex"
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat = os.getenv('TELEGRAM_CHAT_ID')
        self.sent_signals = {}  # address -> timestamp
        self.duplicate_cooldown = timedelta(hours=24)

        # Ensure database exists
        DB_PATH.parent.mkdir(exist_ok=True)
        self._init_db()

        logger.info("🔄 DexScreener Scanner initialized (fallback mode)")
        logger.info(f"   Liquidity min: ${MIN_LIQUIDITY_USD:,.0f}")
        logger.info(f"   Volume 24h min: ${MIN_VOLUME_24H:,.0f}")
        logger.info(f"   Market cap range: ${MIN_MARKET_CAP:,.0f} - ${MAX_MARKET_CAP:,.0f}")

    def _init_db(self):
        """Initialize database if needed"""
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        # Create alerts table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_address TEXT NOT NULL,
                symbol TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                grad_gs INTEGER DEFAULT 0,
                payload TEXT
            )
        """)

        conn.commit()
        conn.close()
        logger.info(f"✅ Database initialized: {DB_PATH}")

    async def fetch_solana_trending(self) -> List[Dict]:
        """Fetch trending Solana pairs from DexScreener"""
        all_pairs = []

        try:
            async with aiohttp.ClientSession() as session:
                # Search for popular Solana tokens
                search_terms = ['SOL', 'USDC', 'BONK', 'WIF', 'PYTH', 'JTO', 'JUP', 'ORCA']

                for term in search_terms:
                    try:
                        url = f"{self.base_url}/search?q={term}"

                        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                            if response.status == 200:
                                data = await response.json()
                                pairs = data.get('pairs', [])

                                # Filter for Solana chain
                                solana_pairs = [p for p in pairs if p.get('chainId') == 'solana']
                                all_pairs.extend(solana_pairs)
                                logger.debug(f"Found {len(solana_pairs)} Solana pairs for {term}")

                            await asyncio.sleep(0.5)  # Rate limiting

                    except Exception as e:
                        logger.debug(f"Error fetching {term}: {e}")
                        continue

                # Remove duplicates by pair address
                unique_pairs = {}
                for pair in all_pairs:
                    pair_addr = pair.get('pairAddress')
                    if pair_addr and pair_addr not in unique_pairs:
                        unique_pairs[pair_addr] = pair

                final_pairs = list(unique_pairs.values())
                logger.info(f"✅ Fetched {len(final_pairs)} unique Solana pairs")
                return final_pairs

        except Exception as e:
            logger.error(f"Error fetching from DexScreener: {e}")
            return []

    def calculate_momentum(self, pair: Dict) -> float:
        """Calculate momentum score for a pair"""
        score = 0

        # Price change weight (max 40 points)
        price_change = float(pair.get('priceChange', {}).get('h24', 0))
        if price_change > 0:
            score += min(price_change * 2, 40)  # Cap at 40

        # Volume weight (max 30 points)
        volume_24h = float(pair.get('volume', {}).get('h24', 0))
        if volume_24h > MIN_VOLUME_24H:
            volume_score = min((volume_24h / 10000) * 5, 30)
            score += volume_score

        # Liquidity weight (max 20 points)
        liquidity = float(pair.get('liquidity', {}).get('usd', 0))
        if liquidity > MIN_LIQUIDITY_USD:
            liquidity_score = min((liquidity / 50000) * 20, 20)
            score += liquidity_score

        # Transaction count weight (max 10 points)
        txns_24h = pair.get('txns', {}).get('h24', {})
        total_txns = txns_24h.get('buys', 0) + txns_24h.get('sells', 0)
        if total_txns > 0:
            score += min(total_txns / 10, 10)

        return round(score, 2)

    def filter_and_rank(self, pairs: List[Dict]) -> List[Dict]:
        """Filter pairs by criteria and rank by momentum"""
        filtered = []

        for pair in pairs:
            # Extract data
            try:
                base_token = pair.get('baseToken', {})
                address = base_token.get('address')
                symbol = base_token.get('symbol', 'UNKNOWN')

                if not address:
                    continue

                # Get metrics
                market_cap = float(pair.get('fdv', 0) or pair.get('marketCap', 0))
                liquidity = float(pair.get('liquidity', {}).get('usd', 0))
                volume_24h = float(pair.get('volume', {}).get('h24', 0))
                price_change_24h = float(pair.get('priceChange', {}).get('h24', 0))

                # Apply filters
                if market_cap < MIN_MARKET_CAP or market_cap > MAX_MARKET_CAP:
                    continue

                if liquidity < MIN_LIQUIDITY_USD:
                    continue

                if volume_24h < MIN_VOLUME_24H:
                    continue

                if price_change_24h < MIN_PRICE_CHANGE_24H:
                    continue

                # Calculate momentum
                momentum = self.calculate_momentum(pair)

                # Check if already sent recently
                if address in self.sent_signals:
                    last_sent = self.sent_signals[address]
                    if datetime.now() - last_sent < self.duplicate_cooldown:
                        logger.debug(f"Skipping {symbol} - already sent recently")
                        continue

                filtered.append({
                    'address': address,
                    'symbol': symbol,
                    'name': base_token.get('name', symbol),
                    'market_cap': market_cap,
                    'liquidity': liquidity,
                    'volume_24h': volume_24h,
                    'price_change_24h': price_change_24h,
                    'momentum': momentum,
                    'pair_address': pair.get('pairAddress'),
                    'dex_id': pair.get('dexId'),
                    'url': pair.get('url'),
                    'price_usd': float(pair.get('priceUsd', 0))
                })

            except Exception as e:
                logger.debug(f"Error processing pair: {e}")
                continue

        # Sort by momentum (highest first)
        filtered.sort(key=lambda x: x['momentum'], reverse=True)

        return filtered

    def store_signal(self, token: Dict) -> bool:
        """Store signal in database"""
        try:
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()

            payload = json.dumps({
                'market_cap': token['market_cap'],
                'liquidity': token['liquidity'],
                'volume_24h': token['volume_24h'],
                'price_change_24h': token['price_change_24h'],
                'momentum': token['momentum'],
                'price_usd': token['price_usd'],
                'dex_id': token.get('dex_id'),
                'url': token.get('url')
            })

            cursor.execute("""
                INSERT INTO alerts (token_address, symbol, grad_gs, payload)
                VALUES (?, ?, ?, ?)
            """, (token['address'], token['symbol'], int(token['momentum']), payload))

            conn.commit()
            conn.close()

            # Mark as sent
            self.sent_signals[token['address']] = datetime.now()

            logger.info(f"✅ Signal stored: {token['symbol']} (momentum: {token['momentum']})")
            return True

        except Exception as e:
            logger.error(f"Error storing signal: {e}")
            return False

    async def send_telegram_alert(self, token: Dict):
        """Send alert to Telegram"""
        if not self.telegram_token or not self.telegram_chat:
            return

        try:
            message = f"""
🚀 <b>New Signal: {token['symbol']}</b>

💎 Market Cap: ${token['market_cap']:,.0f}
💧 Liquidity: ${token['liquidity']:,.0f}
📊 Volume 24h: ${token['volume_24h']:,.0f}
📈 Price Change 24h: {token['price_change_24h']:.2f}%
⚡ Momentum: {token['momentum']:.0f}

🔗 <a href="{token.get('url', '#')}">View on DexScreener</a>
📍 Address: <code>{token['address']}</code>
"""

            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': False
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        logger.info(f"✅ Telegram alert sent for {token['symbol']}")
                    else:
                        logger.error(f"Telegram API error {response.status}")

        except Exception as e:
            logger.error(f"Error sending Telegram alert: {e}")

    async def run_scan_cycle(self) -> int:
        """Run one complete scan cycle"""
        logger.info("=" * 60)
        logger.info("🔍 Starting DexScreener scan cycle...")
        start_time = datetime.now()

        # Fetch trending pairs
        pairs = await self.fetch_solana_trending()

        if not pairs:
            logger.warning("No pairs fetched")
            return 0

        # Filter and rank
        candidates = self.filter_and_rank(pairs)
        logger.info(f"📊 Found {len(candidates)} candidates after filtering")

        # Take top 10
        top_candidates = candidates[:10]
        signals_sent = 0

        for token in top_candidates:
            # Store in database
            if self.store_signal(token):
                # Send Telegram alert
                await self.send_telegram_alert(token)
                signals_sent += 1

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ Scan complete in {duration:.1f}s - Sent {signals_sent} signals")
        logger.info("=" * 60)

        return signals_sent

    async def run_continuous(self):
        """Run scanner continuously"""
        logger.info(f"🔄 Starting continuous scanning (interval: {SCAN_INTERVAL_SECONDS}s)")

        while True:
            try:
                await self.run_scan_cycle()
                await asyncio.sleep(SCAN_INTERVAL_SECONDS)
            except KeyboardInterrupt:
                logger.info("Stopping scanner...")
                break
            except Exception as e:
                logger.error(f"Error in scan cycle: {e}")
                await asyncio.sleep(30)  # Wait 30s on error

async def main():
    """Main entry point"""
    scanner = DexScreenerScanner()
    await scanner.run_continuous()

if __name__ == "__main__":
    asyncio.run(main())
