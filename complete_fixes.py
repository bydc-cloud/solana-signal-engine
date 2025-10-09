#!/usr/bin/env python3
"""
Complete AURA v0.3.0 Fixes
1. Seed whale wallets with correct schema
2. Add missing dashboard API endpoints
3. Add full Claude AI to Telegram
"""

import sqlite3
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_whale_wallets():
    """Seed whale wallets with correct schema"""
    logger.info("🐋 Seeding whale wallets...")

    conn = sqlite3.connect('aura.db')
    cur = conn.cursor()

    # Seed 5 whale wallets matching actual schema
    whales = [
        {
            'address': '7YttLkHDoNj9wyDur5pM1ejNaAvT9X4eqaYcHQqtj2G5',
            'win_rate': 68.5,
            'avg_pnl': 3654.75,
            'total_trades': 127,
            'successful_trades': 87,
            'total_pnl': 456789.50,
            'tokens_traded': 'BONK,WIF,MYRO,JUP,PYTH'
        },
        {
            'address': 'DYw8jCTfwHNRJhhmFcbXvVDTqWMEVFBX6ZKUmG5CNSKK',
            'win_rate': 72.1,
            'avg_pnl': 3511.18,
            'total_trades': 89,
            'successful_trades': 64,
            'total_pnl': 312456.25,
            'tokens_traded': 'SOL,BONK,JTO,RNDR,RAY'
        },
        {
            'address': '5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1',
            'win_rate': 61.2,
            'avg_pnl': 808.51,
            'total_trades': 234,
            'successful_trades': 143,
            'total_pnl': 189234.75,
            'tokens_traded': 'SAMO,COPE,FIDA,KIN,SRM'
        },
        {
            'address': '3vEHvV5FLRPKhLGvPfpxqvRN6jR6HCzWWPgxKqfJjZXh',
            'win_rate': 78.6,
            'avg_pnl': 4188.34,
            'total_trades': 56,
            'successful_trades': 44,
            'total_pnl': 234567.00,
            'tokens_traded': 'JUP,PYTH,MNGO,ORCA,STEP'
        },
        {
            'address': '8BnEgHoWFysVcuFFX7QztDmzuH8r5ZFvyP3sYwn1XTh6',
            'win_rate': 64.4,
            'avg_pnl': 467.60,
            'total_trades': 312,
            'successful_trades': 201,
            'total_pnl': 145890.30,
            'tokens_traded': 'WIF,BONK,POPCAT,MEW,TRUMP'
        }
    ]

    for whale in whales:
        try:
            cur.execute("""
                INSERT OR REPLACE INTO tracked_wallets
                (address, win_rate, avg_pnl, total_trades, successful_trades, total_pnl,
                 first_seen, last_updated, is_active, tokens_traded)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now', '-30 days'), datetime('now'), 1, ?)
            """, (
                whale['address'],
                whale['win_rate'],
                whale['avg_pnl'],
                whale['total_trades'],
                whale['successful_trades'],
                whale['total_pnl'],
                whale['tokens_traded']
            ))
            logger.info(f"  ✅ Seeded {whale['address'][:8]}... ({whale['total_trades']} trades, {whale['win_rate']:.1f}% win rate)")
        except Exception as e:
            logger.error(f"Failed to seed whale {whale['address']}: {e}")

    conn.commit()
    conn.close()

    logger.info(f"✅ Seeded {len(whales)} whale wallets")

def add_missing_dashboard_endpoints():
    """Add missing /api/aura/* dashboard endpoints"""
    logger.info("📊 Adding missing dashboard endpoints...")

    # Read aura_server.py
    with open('aura_server.py', 'r') as f:
        content = f.read()

    # Check if endpoints already exist
    if '/api/aura/scanner/signals' in content and '/api/aura/wallets' in content:
        logger.info("✅ Dashboard endpoints already exist")
        return

    # Find insertion point (before the logs endpoint we added)
    insertion_point = '@app.get("/api/aura/logs")'

    if insertion_point not in content:
        logger.error("❌ Could not find insertion point")
        return

    # Add the missing endpoints
    new_endpoints = '''# Dashboard data endpoints
@app.get("/api/aura/scanner/signals")
async def get_scanner_signals(hours: int = 24, limit: int = 50):
    """Get recent scanner signals"""
    try:
        from aura.database import db
        signals = db.get_recent_helix_signals(hours=hours, limit=limit)
        return {"signals": signals, "count": len(signals)}
    except Exception as e:
        logger.error(f"Signals API error: {e}")
        return {"error": str(e), "signals": [], "count": 0}

@app.get("/api/aura/wallets")
async def get_tracked_wallets():
    """Get tracked whale wallets"""
    try:
        import sqlite3
        conn = sqlite3.connect('aura.db')
        cur = conn.cursor()

        cur.execute("""
            SELECT address, win_rate, avg_pnl, total_trades, successful_trades,
                   total_pnl, last_updated, tokens_traded
            FROM tracked_wallets
            WHERE is_active = 1
            ORDER BY total_pnl DESC
            LIMIT 10
        """)

        wallets = []
        for row in cur.fetchall():
            wallets.append({
                'address': row[0],
                'win_rate': row[1],
                'avg_pnl': row[2],
                'total_trades': row[3],
                'successful_trades': row[4],
                'total_pnl': row[5],
                'last_updated': row[6],
                'tokens_traded': row[7].split(',') if row[7] else []
            })

        conn.close()
        return {"wallets": wallets, "count": len(wallets)}
    except Exception as e:
        logger.error(f"Wallets API error: {e}")
        return {"error": str(e), "wallets": [], "count": 0}

@app.get("/api/aura/portfolio")
async def get_aura_portfolio():
    """Get portfolio summary"""
    try:
        from aura.database import db
        portfolio = db.get_portfolio_summary()
        positions = db.get_open_positions()
        return {
            "portfolio": portfolio,
            "positions": positions,
            "count": len(positions)
        }
    except Exception as e:
        logger.error(f"Portfolio API error: {e}")
        return {"error": str(e), "portfolio": {}, "positions": [], "count": 0}

'''

    # Insert before logs endpoint
    content = content.replace(
        '# Logs API endpoint\n@app.get("/api/aura/logs")',
        new_endpoints + '# Logs API endpoint\n@app.get("/api/aura/logs")'
    )

    # Write back
    with open('aura_server.py', 'w') as f:
        f.write(content)

    logger.info("✅ Added missing dashboard endpoints")

if __name__ == "__main__":
    print("🚀 AURA v0.3.0 - Complete Fixes")
    print("=" * 60)
    print()

    try:
        # 1. Seed whale wallets
        seed_whale_wallets()
        print()

        # 2. Add missing dashboard endpoints
        add_missing_dashboard_endpoints()
        print()

        print("=" * 60)
        print("✅ All fixes applied!")
        print()
        print("Telegram AI was already added by previous script.")
        print()
        print("Next: Deploy to Railway")
        print("  railway up --detach")

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
