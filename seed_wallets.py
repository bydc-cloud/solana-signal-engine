#!/usr/bin/env python3
"""
Seed tracked_wallets table with example whale wallets
"""
import sqlite3
import os
from datetime import datetime

def seed_wallets():
    """Seed the tracked_wallets table"""

    # Connect to database
    db_path = os.path.join(os.path.dirname(__file__), 'aura.db')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Check if table exists
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tracked_wallets'")
    if not cur.fetchone():
        print("❌ tracked_wallets table doesn't exist")
        return

    # Check if already seeded
    cur.execute("SELECT COUNT(*) FROM tracked_wallets")
    existing_count = cur.fetchone()[0]

    if existing_count > 0:
        print(f"ℹ️  tracked_wallets already has {existing_count} entries, skipping seed")
        return

    # Seed with example whale wallets
    wallets = [
        ('7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU', 75.5, 250.0, 42, 32, 10500.0,
         '2025-01-01T00:00:00', datetime.now().isoformat(), 1,
         'BONK,WIF,MYRO,JUP,JTO'),
        ('GUfCR9mK6azb9vcpsxgXyj7XRPAKJd4KMHTTVvtncGgp', 68.2, 180.0, 38, 26, 7020.0,
         '2025-01-15T00:00:00', datetime.now().isoformat(), 1,
         'BONK,ORCA,RAY,SRM,STEP'),
        ('5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1', 82.1, 420.0, 51, 42, 21420.0,
         '2024-12-01T00:00:00', datetime.now().isoformat(), 1,
         'WIF,POPCAT,BONK,JUP,TNSR'),
        ('9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM', 71.8, 310.0, 45, 32, 13950.0,
         '2025-01-20T00:00:00', datetime.now().isoformat(), 1,
         'PYTH,RENDER,BONK,JTO,JUP'),
        ('4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R', 79.3, 390.0, 48, 38, 18720.0,
         '2025-01-10T00:00:00', datetime.now().isoformat(), 1,
         'WIF,MEW,POPCAT,BONK,BOME')
    ]

    cur.executemany("""
        INSERT INTO tracked_wallets
        (address, win_rate, avg_pnl, total_trades, successful_trades, total_pnl,
         first_seen, last_updated, is_active, tokens_traded)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, wallets)

    conn.commit()

    # Verify
    cur.execute("SELECT COUNT(*) FROM tracked_wallets")
    count = cur.fetchone()[0]
    print(f"✅ Seeded {count} whale wallets")

    # Show sample
    cur.execute("SELECT address, win_rate, avg_pnl, total_trades FROM tracked_wallets LIMIT 3")
    print("\n📊 Whale Wallets:")
    for row in cur.fetchall():
        addr_short = f"{row[0][:8]}...{row[0][-4:]}"
        print(f"  • {addr_short} | Win Rate: {row[1]:.1f}% | Avg P&L: ${row[2]:.0f} | Trades: {row[3]}")

    conn.close()


if __name__ == "__main__":
    seed_wallets()
