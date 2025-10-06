"""
AURA Whale Wallet Tracker
Monitors high-value wallets and implements copy trading logic
"""
import logging
import asyncio
import aiohttp
from typing import Dict, List
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)


class WhaleTracker:
    """
    Tracks whale wallets and provides copy trading signals
    - Monitors top SOL holders
    - Tracks their token purchases
    - Generates copy trading signals
    """

    def __init__(self):
        self.helius_key = os.getenv('HELIUS_API_KEY')
        self.birdeye_key = os.getenv('BIRDEYE_API_KEY')

        # List of known whale wallets (top traders, funds, etc.)
        self.monitored_whales = [
            # Add known profitable wallet addresses here
            # These would be discovered through analysis or community intel
        ]

        self.whale_trades = {}  # address -> List[trade_data]
        self.cache_ttl = timedelta(minutes=5)

    async def track_whale_activity(self, whale_address: str) -> List[Dict]:
        """
        Get recent trading activity for a whale wallet
        Returns list of recent token purchases
        """
        try:
            if not self.helius_key:
                logger.warning("No Helius API key for whale tracking")
                return []

            url = f"https://api.helius.xyz/v0/addresses/{whale_address}/transactions"
            params = {
                'api-key': self.helius_key,
                'limit': 50,
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as resp:
                    if resp.status != 200:
                        logger.warning(f"Helius whale tracking error: {resp.status}")
                        return []

                    data = await resp.json()

            trades = []
            for tx in data:
                # Parse transaction for token purchases
                transfers = tx.get('tokenTransfers', [])
                for transfer in transfers:
                    mint = transfer.get('mint')
                    to_address = transfer.get('toUserAccount')
                    amount = transfer.get('tokenAmount', 0)

                    # Check if whale is buying (receiving tokens)
                    if to_address == whale_address and mint:
                        trades.append({
                            'mint': mint,
                            'amount': amount,
                            'timestamp': tx.get('timestamp'),
                            'whale_address': whale_address,
                            'tx_signature': tx.get('signature'),
                        })

            return trades

        except Exception as e:
            logger.error(f"Whale tracking error: {e}")
            return []

    async def get_whale_copy_signals(self) -> List[Dict]:
        """
        Generate copy trading signals based on whale activity
        Returns tokens that whales are buying
        """
        try:
            all_trades = []

            # Track all monitored whales in parallel
            tasks = [
                self.track_whale_activity(whale)
                for whale in self.monitored_whales
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for trades in results:
                if isinstance(trades, Exception):
                    continue
                all_trades.extend(trades)

            # Aggregate by token
            token_signals = {}
            for trade in all_trades:
                mint = trade['mint']
                if mint not in token_signals:
                    token_signals[mint] = {
                        'mint': mint,
                        'whale_count': 0,
                        'total_amount': 0,
                        'recent_buys': [],
                    }

                token_signals[mint]['whale_count'] += 1
                token_signals[mint]['total_amount'] += trade['amount']
                token_signals[mint]['recent_buys'].append(trade)

            # Filter to tokens with multiple whale buyers
            strong_signals = [
                signal for signal in token_signals.values()
                if signal['whale_count'] >= 2
            ]

            return strong_signals

        except Exception as e:
            logger.error(f"Whale copy signals error: {e}")
            return []

    async def discover_new_whales(self, min_sol_balance: float = 1000) -> List[str]:
        """
        Discover new whale wallets based on high SOL holdings
        and successful trading history
        """
        try:
            # In production, use Helius to find top holders
            # and analyze their PnL history
            return []

        except Exception as e:
            logger.error(f"Whale discovery error: {e}")
            return []

    def is_whale_buying(self, token_address: str) -> bool:
        """
        Check if any whales are currently buying a specific token
        """
        try:
            # Check recent whale trades for this token
            for whale_address, trades in self.whale_trades.items():
                for trade in trades:
                    if trade.get('mint') == token_address:
                        # Check if trade is recent (within last hour)
                        trade_time = datetime.fromtimestamp(trade['timestamp'])
                        if datetime.now() - trade_time < timedelta(hours=1):
                            return True

            return False

        except Exception as e:
            logger.error(f"Whale buying check error: {e}")
            return False


# Singleton instance
whale_tracker = WhaleTracker()
