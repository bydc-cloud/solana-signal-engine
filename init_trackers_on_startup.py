#!/usr/bin/env python3
"""
Auto-run on Railway startup to load trackers if database is empty
"""

import sqlite3
import sys
import os

def check_and_load():
    """Check if trackers are loaded, if not, load them"""
    try:
        if not os.path.exists('aura.db'):
            print("Database doesn't exist yet, skipping tracker init")
            return

        conn = sqlite3.connect('aura.db', timeout=10)
        cur = conn.cursor()

        # Check if trackers already loaded
        cur.execute("SELECT COUNT(*) FROM ct_monitors")
        ct_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM live_whale_wallets")
        wallet_count = cur.fetchone()[0]

        if ct_count > 0 and wallet_count > 0:
            print(f"✅ Trackers already loaded: {ct_count} CT, {wallet_count} wallets")
            conn.close()
            return

        print(f"Loading trackers... (current: {ct_count} CT, {wallet_count} wallets)")
        conn.close()

        # Run the batch loading script
        import subprocess
        result = subprocess.run(
            [sys.executable, "LOAD_ALL_TRACKERS_BATCH.py"],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            print("✅ Trackers loaded successfully")
            print(result.stdout)
        else:
            print("❌ Error loading trackers:")
            print(result.stderr)

    except Exception as e:
        print(f"Error in startup init: {e}")

if __name__ == "__main__":
    check_and_load()
