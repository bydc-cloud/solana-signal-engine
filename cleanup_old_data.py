#!/usr/bin/env python3
"""
Database Cleanup Script for Railway Volume Management
Removes old signals and trades to keep database size under control
Run this weekly or monthly via Railway cron
"""

import sqlite3
import os
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
DB_PATH = Path(__file__).parent / "final_nuclear.db"
KEEP_SIGNALS_DAYS = 90  # Keep last 90 days of signals
KEEP_TRADES_DAYS = 180  # Keep last 180 days of trades
DRY_RUN = False  # Set to True to see what would be deleted without deleting

def get_db_size():
    """Get database file size in MB"""
    if not DB_PATH.exists():
        return 0
    return os.path.getsize(DB_PATH) / (1024 * 1024)

def cleanup_old_signals(conn, days=KEEP_SIGNALS_DAYS):
    """Delete signals older than X days"""
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    cur = conn.cursor()

    # Count how many will be deleted
    cur.execute("SELECT COUNT(*) FROM alerts WHERE created_at < ?", (cutoff,))
    count = cur.fetchone()[0]

    if count == 0:
        print(f"✅ No signals older than {days} days")
        return 0

    if DRY_RUN:
        print(f"🔍 DRY RUN: Would delete {count} signals older than {days} days")
        return 0

    # Delete old signals
    cur.execute("DELETE FROM alerts WHERE created_at < ?", (cutoff,))
    conn.commit()

    print(f"🗑️  Deleted {count} signals older than {days} days")
    return count

def cleanup_old_trades(conn, days=KEEP_TRADES_DAYS):
    """Delete trades older than X days"""
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    cur = conn.cursor()

    # Count how many will be deleted
    cur.execute("SELECT COUNT(*) FROM trades WHERE created_at < ?", (cutoff,))
    count = cur.fetchone()[0]

    if count == 0:
        print(f"✅ No trades older than {days} days")
        return 0

    if DRY_RUN:
        print(f"🔍 DRY RUN: Would delete {count} trades older than {days} days")
        return 0

    # Delete old trades
    cur.execute("DELETE FROM trades WHERE created_at < ?", (cutoff,))
    conn.commit()

    print(f"🗑️  Deleted {count} trades older than {days} days")
    return count

def vacuum_database(conn):
    """Reclaim space from deleted records"""
    if DRY_RUN:
        print("🔍 DRY RUN: Would run VACUUM to reclaim space")
        return

    print("🔄 Running VACUUM to reclaim space...")
    conn.execute("VACUUM")
    print("✅ VACUUM complete")

def main():
    print("=" * 60)
    print("Railway Database Cleanup Script")
    print("=" * 60)
    print()

    if DRY_RUN:
        print("⚠️  DRY RUN MODE - No changes will be made")
        print()

    # Check database exists
    if not DB_PATH.exists():
        print(f"❌ Database not found: {DB_PATH}")
        return

    # Get initial size
    size_before = get_db_size()
    print(f"📊 Database size before: {size_before:.2f} MB")
    print()

    # Connect to database
    with sqlite3.connect(DB_PATH) as conn:
        # Cleanup old data
        signals_deleted = cleanup_old_signals(conn, KEEP_SIGNALS_DAYS)
        trades_deleted = cleanup_old_trades(conn, KEEP_TRADES_DAYS)

        # Reclaim space
        if signals_deleted > 0 or trades_deleted > 0:
            vacuum_database(conn)

    # Get final size
    if not DRY_RUN:
        size_after = get_db_size()
        space_saved = size_before - size_after
        print()
        print(f"📊 Database size after: {size_after:.2f} MB")
        print(f"💾 Space saved: {space_saved:.2f} MB ({(space_saved/size_before*100):.1f}%)")

    print()
    print("✅ Cleanup complete!")
    print()

    # Show retention policy
    print("📋 Current retention policy:")
    print(f"   - Signals: {KEEP_SIGNALS_DAYS} days")
    print(f"   - Trades: {KEEP_TRADES_DAYS} days")
    print()

if __name__ == "__main__":
    main()
