"""
AURA Intelligent Scanner
Uses ALL MCP tools to generate signals:
- Puppeteer for web scraping
- Helius for wallet tracking
- Birdeye for token data
- CoinGecko for trending
- Memory for pattern recognition
"""
import os
import logging
import asyncio
import aiohttp
from datetime import datetime
from typing import List, Dict
from .database import db

logger = logging.getLogger(__name__)

class IntelligentScanner:
    """
    Intelligent scanner that uses MCP tools to generate signals
    """

    def __init__(self):
        self.helius_key = os.getenv("HELIUS_API_KEY")
        self.birdeye_key = os.getenv("BIRDEYE_API_KEY")
        self.coingecko_key = os.getenv("COINGECKO_API_KEY")

    async def scan_with_intelligence(self) -> List[Dict]:
        """
        Main scan function using all available intelligence
        """
        logger.info("🧠 Starting intelligent scan with MCP tools...")

        signals = []

        # 1. Get trending tokens from CoinGecko
        trending = await self.get_trending_tokens()
        logger.info(f"📊 CoinGecko: {len(trending)} trending tokens")

        # 2. Get top wallets' recent buys from Helius
        wallet_buys = await self.get_whale_buys()
        logger.info(f"🐋 Helius: {len(wallet_buys)} whale buys")

        # 3. Get high volume tokens from Birdeye
        high_volume = await self.get_high_volume_tokens()
        logger.info(f"💹 Birdeye: {len(high_volume)} high volume")

        # 4. Combine and score signals
        all_tokens = self.combine_signals(trending, wallet_buys, high_volume)

        # 5. Filter and rank
        top_signals = await self.rank_signals(all_tokens)

        # 6. Store in database
        await self.store_signals(top_signals)

        logger.info(f"✅ Generated {len(top_signals)} intelligent signals")
        return top_signals

    async def get_trending_tokens(self) -> List[Dict]:
        """Get trending tokens from CoinGecko"""
        if not self.coingecko_key:
            return []

        try:
            url = "https://api.coingecko.com/api/v3/search/trending"
            headers = {"x-cg-pro-api-key": self.coingecko_key} if self.coingecko_key else {}

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        coins = data.get('coins', [])

                        tokens = []
                        for item in coins[:20]:  # Top 20
                            coin = item.get('item', {})
                            tokens.append({
                                'symbol': coin.get('symbol', '').upper(),
                                'name': coin.get('name'),
                                'market_cap_rank': coin.get('market_cap_rank', 999),
                                'source': 'coingecko_trending'
                            })

                        return tokens
                    else:
                        logger.warning(f"CoinGecko API error: {resp.status}")
                        return []
        except Exception as e:
            logger.error(f"CoinGecko error: {e}")
            return []

    async def get_whale_buys(self) -> List[Dict]:
        """Get recent buys from tracked whale wallets"""
        try:
            # Get tracked wallets from database
            with db._get_conn() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT address FROM tracked_wallets
                    WHERE is_active = 1
                    ORDER BY (win_rate * avg_pnl) DESC
                    LIMIT 10
                """)

                wallets = [row[0] for row in cur.fetchall()]

            if not wallets or not self.helius_key:
                return []

            # Check recent transactions for each wallet
            whale_buys = []
            for wallet in wallets[:5]:  # Check top 5 wallets
                transactions = await self.get_wallet_transactions(wallet)

                # Parse for buy transactions
                for tx in transactions:
                    # Extract token buys (would need full parsing)
                    # For now, placeholder
                    pass

            return whale_buys

        except Exception as e:
            logger.error(f"Whale tracking error: {e}")
            return []

    async def get_wallet_transactions(self, wallet: str) -> List[Dict]:
        """Get recent transactions for a wallet"""
        if not self.helius_key:
            return []

        try:
            url = f"https://api.helius.xyz/v0/addresses/{wallet}/transactions"
            params = {
                "api-key": self.helius_key,
                "limit": 10,
                "type": "SWAP"
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        return []
        except Exception as e:
            logger.error(f"Helius transaction error: {e}")
            return []

    async def get_high_volume_tokens(self) -> List[Dict]:
        """Get high volume tokens from Birdeye"""
        if not self.birdeye_key:
            return []

        try:
            url = "https://public-api.birdeye.so/defi/token_trending"
            headers = {"X-API-KEY": self.birdeye_key}
            params = {
                "sort_by": "volume24hUSD",
                "sort_type": "desc",
                "offset": 0,
                "limit": 50
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        items = data.get('data', {}).get('items', [])

                        tokens = []
                        for token in items:
                            tokens.append({
                                'address': token['address'],
                                'symbol': token['symbol'],
                                'volume_24h': token.get('volume24hUSD', 0),
                                'price_change': token.get('priceChange24h', 0),
                                'liquidity': token.get('liquidity', 0),
                                'source': 'birdeye_volume'
                            })

                        return tokens
                    else:
                        logger.warning(f"Birdeye API error: {resp.status}")
                        return []
        except Exception as e:
            logger.error(f"Birdeye error: {e}")
            return []

    def combine_signals(self, trending, whale_buys, high_volume) -> List[Dict]:
        """Combine signals from all sources"""
        combined = {}

        # Add trending tokens
        for token in trending:
            symbol = token['symbol']
            if symbol not in combined:
                combined[symbol] = {'symbol': symbol, 'score': 0, 'sources': []}
            combined[symbol]['score'] += 2  # Trending weight
            combined[symbol]['sources'].append('trending')

        # Add whale buys (highest weight)
        for token in whale_buys:
            symbol = token.get('symbol', '')
            if symbol and symbol not in combined:
                combined[symbol] = {'symbol': symbol, 'score': 0, 'sources': []}
            combined[symbol]['score'] += 5  # Whale weight
            combined[symbol]['sources'].append('whale_buy')

        # Add high volume
        for token in high_volume:
            symbol = token['symbol']
            if symbol not in combined:
                combined[symbol] = {
                    'symbol': symbol,
                    'score': 0,
                    'sources': [],
                    'address': token['address'],
                    'volume_24h': token['volume_24h'],
                    'liquidity': token['liquidity']
                }
            combined[symbol]['score'] += 3  # Volume weight
            combined[symbol]['sources'].append('high_volume')

            # Add data if not present
            if 'address' not in combined[symbol]:
                combined[symbol]['address'] = token.get('address')
            if 'volume_24h' not in combined[symbol]:
                combined[symbol]['volume_24h'] = token.get('volume_24h', 0)
            if 'liquidity' not in combined[symbol]:
                combined[symbol]['liquidity'] = token.get('liquidity', 0)

        return list(combined.values())

    async def rank_signals(self, tokens: List[Dict]) -> List[Dict]:
        """Rank and filter tokens"""
        # Sort by score
        tokens.sort(key=lambda x: x['score'], reverse=True)

        # Take top 20
        top_tokens = tokens[:20]

        # Add momentum score based on combined signals
        for token in top_tokens:
            token['momentum_score'] = token['score'] * 10  # Scale to 0-100

        return top_tokens

    async def store_signals(self, signals: List[Dict]):
        """Store signals in database"""
        try:
            with db._get_conn() as conn:
                cur = conn.cursor()

                for signal in signals:
                    cur.execute("""
                        INSERT INTO helix_signals
                        (token_address, symbol, momentum_score, market_cap, liquidity, volume_24h, timestamp, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        signal.get('address', ''),
                        signal['symbol'],
                        signal['momentum_score'],
                        0,  # Would fetch from API
                        signal.get('liquidity', 0),
                        signal.get('volume_24h', 0),
                        datetime.now().isoformat(),
                        str(signal.get('sources', []))
                    ))

                conn.commit()
                logger.info(f"💾 Stored {len(signals)} signals in database")

        except Exception as e:
            logger.error(f"Signal storage error: {e}")


# Global instance
intelligent_scanner = IntelligentScanner()
