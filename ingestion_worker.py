#!/usr/bin/env python3
"""
AURA Data Ingestion Worker
Continuously fetches data from DefiLlama, Helius, Birdeye
"""
import os
import time
import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Dict, List

from aura.database import db

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API Keys
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY", "")
BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY", "")

# Endpoints
DEFILLAMA_BASE = "https://api.llama.fi"
HELIUS_RPC = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"
BIRDEYE_BASE = "https://public-api.birdeye.so"


class DefiLlamaIngester:
    """Fetches TVL data from DefiLlama"""

    async def fetch_tvl(self, protocol: str, session: aiohttp.ClientSession) -> Dict:
        """Fetch TVL for a protocol"""
        try:
            url = f"{DEFILLAMA_BASE}/protocol/{protocol}"
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception as e:
            logger.error(f"DefiLlama fetch error: {e}")
        return {}

    async def upsert_tvl(self, token_address: str, tvl_usd: float, liquidity_usd: float, source: str = "defillama"):
        """Upsert TVL data into database"""
        try:
            timestamp = int(time.time())
            with db._get_conn() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT OR REPLACE INTO token_tvl
                    (token_address, tvl_usd, liquidity_usd, timestamp, source)
                    VALUES (?, ?, ?, ?, ?)
                """, (token_address, tvl_usd, liquidity_usd, timestamp, source))
                conn.commit()
        except Exception as e:
            logger.error(f"TVL upsert error: {e}")

    async def run_cycle(self) -> int:
        """Run ingestion cycle for DefiLlama"""
        try:
            # Get top Solana protocols
            protocols = ["uniswap", "raydium", "jupiter", "orca", "marinade-finance"]

            async with aiohttp.ClientSession() as session:
                upserted = 0
                for protocol in protocols:
                    data = await self.fetch_tvl(protocol, session)
                    if data and "tvl" in data:
                        # Use protocol name as address placeholder
                        solana_tvl = data.get("chainTvls", {}).get("Solana", 0)
                        await self.upsert_tvl(protocol, data["tvl"], solana_tvl)
                        upserted += 1

                logger.info(f"📊 DefiLlama: Upserted {upserted} TVL records")
                return upserted

        except Exception as e:
            logger.error(f"DefiLlama cycle error: {e}")
            return 0


class HeliusIngester:
    """Fetches transaction data from Helius"""

    async def fetch_transactions(self, address: str, session: aiohttp.ClientSession) -> List[Dict]:
        """Fetch recent transactions for address"""
        try:
            if not HELIUS_API_KEY:
                return []

            # Use Helius Enhanced Transactions API
            url = f"https://api.helius.xyz/v0/addresses/{address}/transactions?api-key={HELIUS_API_KEY}"
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("transactions", [])
        except Exception as e:
            logger.debug(f"Helius fetch error: {e}")
        return []

    async def run_cycle(self) -> int:
        """Run ingestion cycle for Helius"""
        try:
            if not HELIUS_API_KEY:
                logger.debug("Helius API key not set, skipping")
                return 0

            # Get tracked tokens
            watchlist = db.get_watchlist()

            if not watchlist:
                return 0

            async with aiohttp.ClientSession() as session:
                upserted = 0
                for item in watchlist[:10]:  # Top 10 watchlist tokens
                    address = item["token_address"]
                    txs = await self.fetch_transactions(address, session)

                    if txs:
                        # Store as fact
                        fact = f"Recent activity: {len(txs)} transactions in last hour"
                        db.add_token_fact(address, "technical", fact, "helius", 0.9)
                        upserted += 1

                logger.info(f"⛓️  Helius: Upserted {upserted} transaction facts")
                return upserted

        except Exception as e:
            logger.error(f"Helius cycle error: {e}")
            return 0


class BirdeyeIngester:
    """Fetches OHLCV data from Birdeye"""

    async def fetch_ohlcv(self, address: str, timeframe: str, session: aiohttp.ClientSession) -> List[Dict]:
        """Fetch OHLCV data"""
        try:
            if not BIRDEYE_API_KEY:
                return []

            # Birdeye OHLCV endpoint
            url = f"{BIRDEYE_BASE}/defi/ohlcv"
            params = {
                "address": address,
                "type": timeframe,  # '1m', '5m', '15m', '1h', '4h', '1d'
            }
            headers = {"X-API-KEY": BIRDEYE_API_KEY}

            async with session.get(url, params=params, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("data", {}).get("items", [])
        except Exception as e:
            logger.debug(f"Birdeye fetch error: {e}")
        return []

    async def upsert_ohlc(self, token_address: str, timeframe: str, ohlc_data: List[Dict]):
        """Upsert OHLC data into database"""
        try:
            with db._get_conn() as conn:
                cur = conn.cursor()
                for candle in ohlc_data:
                    cur.execute("""
                        INSERT OR REPLACE INTO token_price_ohlc
                        (token_address, timeframe, timestamp, open, high, low, close, volume_usd, source)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'birdeye')
                    """, (
                        token_address,
                        timeframe,
                        candle["unixTime"],
                        candle["o"],
                        candle["h"],
                        candle["l"],
                        candle["c"],
                        candle.get("v", 0)
                    ))
                conn.commit()
        except Exception as e:
            logger.error(f"OHLC upsert error: {e}")

    async def run_cycle(self) -> int:
        """Run ingestion cycle for Birdeye"""
        try:
            if not BIRDEYE_API_KEY:
                logger.debug("Birdeye API key not set, skipping")
                return 0

            # Get tracked tokens
            watchlist = db.get_watchlist()

            if not watchlist:
                return 0

            timeframes = ["1m", "5m", "1h"]

            async with aiohttp.ClientSession() as session:
                upserted = 0
                for item in watchlist[:5]:  # Top 5 watchlist tokens
                    address = item["token_address"]

                    for tf in timeframes:
                        ohlc = await self.fetch_ohlcv(address, tf, session)
                        if ohlc:
                            await self.upsert_ohlc(address, tf, ohlc)
                            upserted += len(ohlc)

                logger.info(f"📈 Birdeye: Upserted {upserted} OHLC candles")
                return upserted

        except Exception as e:
            logger.error(f"Birdeye cycle error: {e}")
            return 0


async def main():
    """Main worker loop"""
    logger.info("🔄 AURA Ingestion Worker starting...")
    logger.info("📊 Data sources: DefiLlama, Helius, Birdeye")

    # Check API keys
    if not HELIUS_API_KEY:
        logger.warning("⚠️  HELIUS_API_KEY not set - Helius ingestion disabled")
    if not BIRDEYE_API_KEY:
        logger.warning("⚠️  BIRDEYE_API_KEY not set - Birdeye ingestion disabled")

    defillama = DefiLlamaIngester()
    helius = HeliusIngester()
    birdeye = BirdeyeIngester()

    cycle_count = 0

    while True:
        try:
            cycle_count += 1
            start = time.time()

            logger.info(f"🔄 Ingestion Cycle #{cycle_count} - {datetime.now().isoformat()}")

            # Run all ingesters in parallel
            results = await asyncio.gather(
                defillama.run_cycle(),
                helius.run_cycle(),
                birdeye.run_cycle(),
                return_exceptions=True
            )

            elapsed = time.time() - start
            total_records = sum(r for r in results if isinstance(r, int))

            logger.info(f"✅ Cycle complete: {total_records} records in {elapsed:.2f}s")

            # Wait 60 seconds between cycles
            await asyncio.sleep(60)

        except KeyboardInterrupt:
            logger.info("🛑 Ingestion worker stopping...")
            break
        except Exception as e:
            logger.error(f"❌ Ingestion worker error: {e}")
            await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())
