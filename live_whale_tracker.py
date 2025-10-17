#!/usr/bin/env python3
"""
LIVE Whale Wallet Tracker
Continuously monitors ALL 162 whale wallets in real-time using Helius
Tracks trades, calculates win rates, and stores in database
"""

import os
import asyncio
import aiohttp
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HELIUS_API_KEY = os.getenv('HELIUS_API_KEY', '')

class LiveWhaleTracker:
    def __init__(self, db_path='aura.db'):
        self.db_path = db_path
        self.session = None

    async def init(self):
        self.session = aiohttp.ClientSession()

    async def close(self):
        if self.session:
            await self.session.close()

    async def fetch_wallet_transactions(self, wallet_address: str, limit: int = 50) -> List[Dict]:
        """Fetch recent transactions for a wallet using Helius"""
        if not HELIUS_API_KEY:
            logger.error("HELIUS_API_KEY not set!")
            return []

        url = f"https://api.helius.xyz/v0/addresses/{wallet_address}/transactions"
        params = {
            'api-key': HELIUS_API_KEY,
            'limit': limit
        }

        try:
            async with self.session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    logger.error(f"Helius API error {response.status} for {wallet_address}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching {wallet_address}: {e}")
            return []

    def parse_swap_transaction(self, tx: Dict) -> Optional[Dict]:
        """Parse a transaction to extract swap/trade info"""
        try:
            # Get transaction type
            tx_type = tx.get('type', '')
            timestamp = tx.get('timestamp', 0)
            signature = tx.get('signature', '')

            # Look for swap/token transfer data
            token_transfers = tx.get('tokenTransfers', [])
            native_transfers = tx.get('nativeTransfers', [])

            if not token_transfers and not native_transfers:
                return None

            # Simple swap detection: if SOL out + token in = BUY, token out + SOL in = SELL
            sol_delta = 0
            token_delta = {}

            for transfer in native_transfers:
                if transfer.get('fromUserAccount') == tx.get('feePayer'):
                    sol_delta -= transfer.get('amount', 0) / 1e9
                if transfer.get('toUserAccount') == tx.get('feePayer'):
                    sol_delta += transfer.get('amount', 0) / 1e9

            for transfer in token_transfers:
                token_addr = transfer.get('mint', '')
                amount = transfer.get('tokenAmount', 0)

                if transfer.get('fromUserAccount') == tx.get('feePayer'):
                    token_delta[token_addr] = token_delta.get(token_addr, 0) - amount
                if transfer.get('toUserAccount') == tx.get('feePayer'):
                    token_delta[token_addr] = token_delta.get(token_addr, 0) + amount

            # Determine trade type
            if sol_delta < 0 and any(v > 0 for v in token_delta.values()):
                # Spent SOL, got tokens = BUY
                trade_type = 'buy'
                token_addr = next((k for k, v in token_delta.items() if v > 0), None)
                sol_amount = abs(sol_delta)
            elif sol_delta > 0 and any(v < 0 for v in token_delta.values()):
                # Got SOL, spent tokens = SELL
                trade_type = 'sell'
                token_addr = next((k for k, v in token_delta.items() if v < 0), None)
                sol_amount = sol_delta
            else:
                return None

            if not token_addr:
                return None

            return {
                'type': trade_type,
                'token_address': token_addr,
                'sol_amount': sol_amount,
                'timestamp': datetime.fromtimestamp(timestamp).isoformat(),
                'signature': signature
            }

        except Exception as e:
            logger.error(f"Error parsing transaction: {e}")
            return None

    def store_trade(self, wallet_address: str, trade: Dict):
        """Store a trade in the database"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        try:
            cur.execute("""
                INSERT OR IGNORE INTO whale_transactions
                (wallet_address, token_address, type, value_usd, timestamp, tx_signature)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                wallet_address,
                trade['token_address'],
                trade['type'],
                trade['sol_amount'] * 150,  # Rough USD estimate
                trade['timestamp'],
                trade['signature']
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Error storing trade: {e}")
        finally:
            conn.close()

    def update_wallet_stats(self, wallet_address: str):
        """Calculate and update stats for a wallet based on trades"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        try:
            # Get all trades for this wallet
            cur.execute("""
                SELECT token_address, type, value_usd, timestamp
                FROM whale_transactions
                WHERE wallet_address = ?
                ORDER BY timestamp ASC
            """, (wallet_address,))

            trades = cur.fetchall()

            if not trades:
                return

            # Track positions by token
            positions = {}  # token -> {'entry': price, 'amount': amount}
            closed_trades = []

            for token, trade_type, value, timestamp in trades:
                if trade_type == 'buy':
                    if token not in positions:
                        positions[token] = {'entries': [], 'total_cost': 0}
                    positions[token]['entries'].append({'value': value, 'timestamp': timestamp})
                    positions[token]['total_cost'] += value
                elif trade_type == 'sell':
                    if token in positions and positions[token]['entries']:
                        # Calculate PnL (simplified: FIFO)
                        entry = positions[token]['entries'].pop(0)
                        pnl = value - entry['value']
                        closed_trades.append({
                            'token': token,
                            'pnl': pnl,
                            'pnl_percent': (pnl / entry['value'] * 100) if entry['value'] > 0 else 0,
                            'timestamp': timestamp
                        })

            # Calculate stats
            total_trades = len(closed_trades)
            if total_trades == 0:
                return

            winning_trades = sum(1 for t in closed_trades if t['pnl'] > 0)
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            total_pnl = sum(t['pnl'] for t in closed_trades)
            last_trade = closed_trades[-1]['timestamp'] if closed_trades else None

            # Update stats table
            cur.execute("""
                INSERT OR REPLACE INTO whale_stats
                (wallet_address, total_trades, winning_trades, win_rate, total_pnl_usd, last_trade_timestamp, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                wallet_address,
                total_trades,
                winning_trades,
                round(win_rate, 1),
                round(total_pnl, 2),
                last_trade,
                datetime.now().isoformat()
            ))

            conn.commit()
            logger.info(f"✅ Updated stats for {wallet_address}: {total_trades} trades, {win_rate:.1f}% WR")

        except Exception as e:
            logger.error(f"Error updating stats: {e}")
        finally:
            conn.close()

    async def track_wallet(self, wallet_address: str, nickname: str):
        """Track a single wallet - fetch recent trades and update stats"""
        try:
            logger.info(f"📡 Tracking {nickname} ({wallet_address[:8]}...)")

            # Fetch recent transactions
            transactions = await self.fetch_wallet_transactions(wallet_address, limit=100)

            if not transactions:
                logger.warning(f"No transactions for {nickname}")
                return

            # Parse and store trades
            trades_found = 0
            for tx in transactions:
                trade = self.parse_swap_transaction(tx)
                if trade:
                    self.store_trade(wallet_address, trade)
                    trades_found += 1

            if trades_found > 0:
                # Update statistics
                self.update_wallet_stats(wallet_address)
                logger.info(f"✅ {nickname}: Found {trades_found} trades")
            else:
                logger.info(f"⚪ {nickname}: No swaps found in recent txs")

        except Exception as e:
            logger.error(f"Error tracking {nickname}: {e}")

    async def track_all_wallets(self):
        """Track ALL wallets in parallel"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Get all wallets
        cur.execute("SELECT wallet_address, nickname FROM live_whale_wallets")
        wallets = cur.fetchall()
        conn.close()

        logger.info(f"🚀 Starting tracking for {len(wallets)} wallets...")

        # Track in batches to avoid rate limits
        batch_size = 10
        for i in range(0, len(wallets), batch_size):
            batch = wallets[i:i+batch_size]
            tasks = [self.track_wallet(addr, nick) for addr, nick in batch]
            await asyncio.gather(*tasks)

            # Small delay between batches
            if i + batch_size < len(wallets):
                await asyncio.sleep(2)

        logger.info(f"✅ Completed tracking all {len(wallets)} wallets!")

async def main():
    tracker = LiveWhaleTracker()
    await tracker.init()

    try:
        await tracker.track_all_wallets()
    finally:
        await tracker.close()

if __name__ == "__main__":
    asyncio.run(main())
