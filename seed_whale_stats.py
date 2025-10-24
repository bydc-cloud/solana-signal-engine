#!/usr/bin/env python3
"""
Seed some realistic whale performance stats for demonstration
"""

import sqlite3
from datetime import datetime, timedelta
import random

def seed_whale_stats():
    conn = sqlite3.connect('aura.db')
    cur = conn.cursor()

    # Create whale_stats table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS whale_stats (
            wallet_address TEXT PRIMARY KEY,
            total_trades INTEGER DEFAULT 0,
            winning_trades INTEGER DEFAULT 0,
            win_rate REAL DEFAULT 0,
            total_pnl_usd REAL DEFAULT 0,
            last_trade_timestamp TEXT,
            updated_at TEXT
        )
    """)

    # Get top wallets
    cur.execute("SELECT wallet_address, nickname FROM live_whale_wallets LIMIT 20")
    wallets = cur.fetchall()

    print(f"📊 Seeding stats for {len(wallets)} top wallets...")

    for wallet_addr, nickname in wallets:
        # Generate realistic stats
        total_trades = random.randint(5, 50)
        win_rate = random.uniform(45, 75)  # 45-75% win rate
        winning_trades = int(total_trades * (win_rate / 100))

        # Calculate PnL (winners make more than losers lose)
        avg_win = random.uniform(500, 5000)
        avg_loss = random.uniform(200, 1000)
        total_pnl = (winning_trades * avg_win) - ((total_trades - winning_trades) * avg_loss)

        last_trade = datetime.now() - timedelta(days=random.randint(0, 7))

        cur.execute("""
            INSERT OR REPLACE INTO whale_stats
            (wallet_address, total_trades, winning_trades, win_rate, total_pnl_usd, last_trade_timestamp, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            wallet_addr,
            total_trades,
            winning_trades,
            round(win_rate, 1),
            round(total_pnl, 2),
            last_trade.isoformat(),
            datetime.now().isoformat()
        ))

        print(f"  ✓ {nickname}: {total_trades} trades, {win_rate:.1f}% win rate, ${total_pnl:,.0f} PnL")

    conn.commit()
    conn.close()
    print(f"\n✅ Seeded stats for {len(wallets)} wallets!")

if __name__ == "__main__":
    seed_whale_stats()
