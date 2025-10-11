#!/usr/bin/env python3
"""
AURA Live System - Transform from Conceptual to Operational
Real-time data connections, active monitoring, and live analysis
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
import aiohttp
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient

logger = logging.getLogger(__name__)


class LiveMarketConnection:
    """Real-time connection to Solana blockchain and DEXs"""

    def __init__(self):
        # Load from env file if not in environment
        from dotenv import load_dotenv
        load_dotenv()

        self.helius_key = os.getenv("HELIUS_API_KEY")
        self.birdeye_key = os.getenv("BIRDEYE_API_KEY")

        if not self.helius_key:
            logger.warning("⚠️  HELIUS_API_KEY not found - using fallback RPC")
            self.rpc_url = "https://api.mainnet-beta.solana.com"
        else:
            self.rpc_url = f"https://mainnet.helius-rpc.com/?api-key={self.helius_key}"

        self.solana_client = AsyncClient(self.rpc_url)

        # Connection status
        self.connected = False
        self.last_update = None
        self.connection_quality = "Unknown"

        logger.info("🔌 Initializing live market connections...")

    async def connect(self) -> bool:
        """Establish live connection to blockchain"""
        try:
            # Test Solana RPC connection
            response = await self.solana_client.get_slot()
            if response.value:
                self.connected = True
                self.last_update = datetime.now()
                self.connection_quality = "Excellent"
                logger.info(f"✅ Connected to Solana mainnet (slot: {response.value})")
                return True
            else:
                raise Exception("No response from RPC")

        except Exception as e:
            self.connected = False
            self.connection_quality = "Disconnected"
            logger.error(f"❌ Failed to connect to Solana: {e}")
            return False

    async def get_current_slot(self) -> int:
        """Get current Solana blockchain slot (real-time)"""
        try:
            response = await self.solana_client.get_slot()
            return response.value
        except Exception as e:
            logger.error(f"Error getting slot: {e}")
            return 0

    async def get_token_price_live(self, token_address: str) -> Optional[float]:
        """Get real-time token price from Birdeye"""
        try:
            url = f"https://public-api.birdeye.so/defi/price?address={token_address}"
            headers = {"X-API-KEY": self.birdeye_key}

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        price = data.get("data", {}).get("value")
                        if price:
                            logger.info(f"💰 Live price for {token_address[:8]}...: ${price}")
                            return float(price)
        except Exception as e:
            logger.error(f"Error fetching live price: {e}")

        return None

    async def get_dex_liquidity_live(self, token_address: str) -> Dict:
        """Get real-time liquidity data from DEXs"""
        try:
            url = f"https://public-api.birdeye.so/defi/v3/token/liquidity?address={token_address}"
            headers = {"X-API-KEY": self.birdeye_key}

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("data", {})
        except Exception as e:
            logger.error(f"Error fetching liquidity: {e}")

        return {}

    async def monitor_wallet_live(self, wallet_address: str) -> List[Dict]:
        """Monitor whale wallet in real-time using Helius"""
        try:
            url = f"https://api.helius.xyz/v0/addresses/{wallet_address}/transactions"
            params = {"api-key": self.helius_key, "limit": 10}

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        transactions = await response.json()
                        logger.info(f"🐋 Monitored {len(transactions)} recent txs for {wallet_address[:8]}...")
                        return transactions
        except Exception as e:
            logger.error(f"Error monitoring wallet: {e}")

        return []

    def get_status(self) -> Dict:
        """Get current connection status"""
        return {
            "connected": self.connected,
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "connection_quality": self.connection_quality,
            "rpc_endpoint": "Helius Mainnet",
            "data_sources": ["Solana RPC", "Birdeye API", "Helius API"]
        }


class LiveMomentumEngine:
    """Real-time momentum scoring and analysis"""

    def __init__(self, market_connection: LiveMarketConnection):
        self.market = market_connection
        self.active_signals = 0
        self.last_scan = None

    async def calculate_momentum_live(self, token_address: str) -> Dict:
        """Calculate real-time momentum score"""
        try:
            logger.info(f"📊 Calculating live momentum for {token_address[:8]}...")

            # Get real-time price
            price = await self.market.get_token_price_live(token_address)

            # Get liquidity data
            liquidity_data = await self.market.get_dex_liquidity_live(token_address)

            # Calculate momentum components
            volume_24h = liquidity_data.get("v24hUSD", 0)
            buy_volume = liquidity_data.get("buy24hUSD", 0)
            sell_volume = liquidity_data.get("sell24hUSD", 0)

            # Calculate buyer dominance
            total_volume = buy_volume + sell_volume
            buyer_dominance = (buy_volume / total_volume * 100) if total_volume > 0 else 50

            # Calculate momentum score (0-100)
            momentum_score = 0

            # Volume factor (0-40 points)
            if volume_24h > 1000000:  # > $1M
                momentum_score += 40
            elif volume_24h > 500000:  # > $500k
                momentum_score += 30
            elif volume_24h > 100000:  # > $100k
                momentum_score += 20

            # Buyer dominance factor (0-40 points)
            if buyer_dominance > 70:
                momentum_score += 40
            elif buyer_dominance > 60:
                momentum_score += 30
            elif buyer_dominance > 55:
                momentum_score += 20

            # Liquidity factor (0-20 points)
            liquidity = liquidity_data.get("liquidity", 0)
            if liquidity > 500000:  # > $500k
                momentum_score += 20
            elif liquidity > 250000:  # > $250k
                momentum_score += 15
            elif liquidity > 100000:  # > $100k
                momentum_score += 10

            self.last_scan = datetime.now()

            result = {
                "token_address": token_address,
                "momentum_score": momentum_score,
                "price_usd": price,
                "volume_24h": volume_24h,
                "buyer_dominance": buyer_dominance,
                "liquidity": liquidity,
                "timestamp": datetime.now().isoformat(),
                "confidence": "HIGH" if momentum_score > 70 else "MEDIUM" if momentum_score > 50 else "LOW"
            }

            logger.info(f"✅ Momentum: {momentum_score}/100 (confidence: {result['confidence']})")

            return result

        except Exception as e:
            logger.error(f"Error calculating momentum: {e}")
            return {"error": str(e)}


class LiveWhalTracker:
    """Real-time whale wallet monitoring"""

    def __init__(self, market_connection: LiveMarketConnection):
        self.market = market_connection
        self.tracked_wallets = []
        self.recent_activities = []

    async def track_whale_live(self, wallet_address: str) -> Dict:
        """Track whale wallet in real-time"""
        try:
            logger.info(f"🐋 Tracking whale {wallet_address[:8]}... in real-time")

            # Get recent transactions
            transactions = await self.market.monitor_wallet_live(wallet_address)

            # Analyze transaction patterns
            buys = []
            sells = []

            for tx in transactions:
                # Parse transaction type
                tx_type = tx.get("type", "unknown")
                if "buy" in tx_type.lower() or "swap" in tx_type.lower():
                    buys.append(tx)
                elif "sell" in tx_type.lower():
                    sells.append(tx)

            result = {
                "wallet_address": wallet_address,
                "recent_buys": len(buys),
                "recent_sells": len(sells),
                "total_transactions": len(transactions),
                "activity_score": len(transactions) * 10,
                "last_activity": transactions[0].get("timestamp") if transactions else None,
                "timestamp": datetime.now().isoformat()
            }

            logger.info(f"✅ Whale activity: {result['recent_buys']} buys, {result['recent_sells']} sells")

            return result

        except Exception as e:
            logger.error(f"Error tracking whale: {e}")
            return {"error": str(e)}


class AuraLiveSystem:
    """
    Complete live AURA system - transforms conceptual to operational
    """

    def __init__(self):
        self.market = LiveMarketConnection()
        self.momentum_engine = LiveMomentumEngine(self.market)
        self.whale_tracker = LiveWhalTracker(self.market)

        self.system_status = "Initializing"
        self.start_time = datetime.now()

    async def initialize(self) -> bool:
        """Initialize all live connections"""
        logger.info("🚀 Starting AURA Live System...")

        # Connect to blockchain
        connected = await self.market.connect()

        if connected:
            self.system_status = "Operational"
            logger.info("✅ AURA Live System is OPERATIONAL")
            return True
        else:
            self.system_status = "Disconnected"
            logger.error("❌ Failed to initialize AURA Live System")
            return False

    async def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        market_status = self.market.get_status()

        uptime = (datetime.now() - self.start_time).total_seconds()

        return {
            "system_status": self.system_status,
            "uptime_seconds": uptime,
            "market_connection": market_status,
            "active_signals": self.momentum_engine.active_signals,
            "last_scan": self.momentum_engine.last_scan.isoformat() if self.momentum_engine.last_scan else None,
            "data_sources": [
                "Solana RPC (Helius)",
                "Birdeye DEX API",
                "Helius Transaction API"
            ],
            "capabilities": [
                "Real-time price feeds",
                "Live momentum scoring",
                "Whale wallet tracking",
                "Transaction monitoring",
                "Liquidity analysis"
            ],
            "timestamp": datetime.now().isoformat()
        }

    async def analyze_token_live(self, token_address: str) -> Dict:
        """Perform live analysis on a token"""
        logger.info(f"🔍 Live analysis for token: {token_address}")

        # Get momentum data
        momentum = await self.momentum_engine.calculate_momentum_live(token_address)

        # Build comprehensive analysis
        analysis = {
            "token_address": token_address,
            "analysis_type": "LIVE",
            "momentum": momentum,
            "data_sources": ["Birdeye", "Solana RPC"],
            "timestamp": datetime.now().isoformat(),
            "system_status": self.system_status
        }

        return analysis

    async def monitor_whale_activity(self, wallet_address: str) -> Dict:
        """Monitor whale wallet activity"""
        return await self.whale_tracker.track_whale_live(wallet_address)


# Global instance
live_system = None


async def get_live_system() -> AuraLiveSystem:
    """Get or create live system instance"""
    global live_system

    if live_system is None:
        live_system = AuraLiveSystem()
        await live_system.initialize()

    return live_system


# CLI for testing
async def main():
    """Test the live system"""
    print("🚀 AURA Live System Test\n")

    system = await get_live_system()

    # Get system status
    status = await system.get_system_status()
    print("📊 System Status:")
    print(f"  Status: {status['system_status']}")
    print(f"  Connected: {status['market_connection']['connected']}")
    print(f"  Quality: {status['market_connection']['connection_quality']}")
    print(f"  Data Sources: {', '.join(status['data_sources'])}")
    print()

    # Test with a known Solana token (e.g., BONK)
    bonk_address = "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"

    print(f"🔍 Analyzing BONK token live...\n")
    analysis = await system.analyze_token_live(bonk_address)

    if "error" not in analysis.get("momentum", {}):
        print("✅ Live Analysis Results:")
        momentum = analysis["momentum"]
        print(f"  Momentum Score: {momentum.get('momentum_score')}/100")
        print(f"  Price: ${momentum.get('price_usd')}")
        print(f"  Volume 24h: ${momentum.get('volume_24h'):,.0f}")
        print(f"  Buyer Dominance: {momentum.get('buyer_dominance'):.1f}%")
        print(f"  Confidence: {momentum.get('confidence')}")

    await system.market.solana_client.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
