#!/usr/bin/env python3
"""
Railway initialization script
Run this on Railway to seed database and start scanner
"""

import sqlite3
import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_whale_wallets():
    """Seed whale wallets"""
    logger.info("🐋 Seeding whale wallets...")

    conn = sqlite3.connect('aura.db')
    cur = conn.cursor()

    # Create table if not exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tracked_wallets (
            address TEXT PRIMARY KEY,
            win_rate REAL DEFAULT 0,
            avg_pnl REAL DEFAULT 0,
            total_trades INTEGER DEFAULT 0,
            successful_trades INTEGER DEFAULT 0,
            total_pnl REAL DEFAULT 0,
            first_seen TEXT,
            last_updated TEXT,
            is_active INTEGER DEFAULT 1,
            tokens_traded TEXT
        )
    """)

    whales = [
        ('7YttLkHDoNj9wyDur5pM1ejNaAvT9X4eqaYcHQqtj2G5', 68.5, 3654.75, 127, 87, 456789.50, 'BONK,WIF,MYRO,JUP,PYTH'),
        ('DYw8jCTfwHNRJhhmFcbXvVDTqWMEVFBX6ZKUmG5CNSKK', 72.1, 3511.18, 89, 64, 312456.25, 'SOL,BONK,JTO,RNDR,RAY'),
        ('5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1', 61.2, 808.51, 234, 143, 189234.75, 'SAMO,COPE,FIDA,KIN,SRM'),
        ('3vEHvV5FLRPKhLGvPfpxqvRN6jR6HCzWWPgxKqfJjZXh', 78.6, 4188.34, 56, 44, 234567.00, 'JUP,PYTH,MNGO,ORCA,STEP'),
        ('8BnEgHoWFysVcuFFX7QztDmzuH8r5ZFvyP3sYwn1XTh6', 64.4, 467.60, 312, 201, 145890.30, 'WIF,BONK,POPCAT,MEW,TRUMP')
    ]

    for whale in whales:
        cur.execute("""
            INSERT OR REPLACE INTO tracked_wallets
            (address, win_rate, avg_pnl, total_trades, successful_trades, total_pnl,
             first_seen, last_updated, is_active, tokens_traded)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now', '-30 days'), datetime('now'), 1, ?)
        """, whale)

    conn.commit()
    conn.close()

    logger.info(f"✅ Seeded {len(whales)} whale wallets")

def start_scanner():
    """Start scanner in background"""
    logger.info("🚀 Starting scanner...")

    try:
        # Check if already running
        result = subprocess.run(['pgrep', '-f', 'REALITY_MOMENTUM_SCANNER.py'],
                                capture_output=True, text=True)

        if result.returncode == 0:
            logger.info("Scanner already running")
            return

        # Start scanner
        subprocess.Popen(['python3', 'REALITY_MOMENTUM_SCANNER.py'],
                         stdout=open('scanner.log', 'w'),
                         stderr=subprocess.STDOUT)

        logger.info("✅ Scanner started")

    except Exception as e:
        logger.error(f"Failed to start scanner: {e}")

if __name__ == "__main__":
    print("🚀 Railway Initialization")
    print("=" * 50)
    print()

    try:
        seed_whale_wallets()
        print()
        start_scanner()
        print()
        print("=" * 50)
        print("✅ Railway initialization complete!")

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)
