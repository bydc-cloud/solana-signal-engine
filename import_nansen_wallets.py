#!/usr/bin/env python3
"""
Import Top Whale Wallets from Nansen
Fetches 174+ top Solana wallets and imports to AURA database
"""
import requests
import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

NANSEN_API_KEY = os.getenv('NASEN_API_KEY')  # Note: typo in .env but using as-is
DB_PATH = "aura.db"

def fetch_nansen_wallets():
    """Fetch top Solana wallets from Nansen"""
    headers = {
        'X-API-KEY': NANSEN_API_KEY
    }

    # Nansen endpoints for Solana smart money
    endpoints = [
        # Smart money wallets
        'https://api.nansen.ai/v1/solana/wallets/smart-money',
        # Top traders
        'https://api.nansen.ai/v1/solana/wallets/top-traders',
        # Whale wallets
        'https://api.nansen.ai/v1/solana/wallets/whales',
    ]

    all_wallets = []

    for endpoint in endpoints:
        try:
            print(f"Fetching from: {endpoint}")
            response = requests.get(
                endpoint,
                headers=headers,
                params={'limit': 100, 'chain': 'solana'},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                wallets = data.get('wallets', data.get('data', []))
                print(f"✅ Found {len(wallets)} wallets")
                all_wallets.extend(wallets)
            else:
                print(f"⚠️ HTTP {response.status_code}: {response.text[:200]}")
        except Exception as e:
            print(f"❌ Error fetching {endpoint}: {e}")

    return all_wallets

def import_wallets_to_aura(wallets):
    """Import wallets to AURA database"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    imported = 0
    skipped = 0

    for wallet in wallets:
        try:
            # Extract wallet data (flexible for different API responses)
            address = wallet.get('address') or wallet.get('wallet') or wallet.get('id')
            if not address:
                continue

            nickname = wallet.get('label') or wallet.get('name') or wallet.get('nickname')
            metadata = {
                'source': 'nansen',
                'balance': wallet.get('balance'),
                'pnl': wallet.get('pnl'),
                'win_rate': wallet.get('win_rate'),
                'category': wallet.get('category'),
                'tags': wallet.get('tags', [])
            }

            cur.execute("""
                INSERT INTO tracked_wallets (
                    address, nickname, first_seen, last_updated, is_active, metadata
                ) VALUES (?, ?, ?, ?, 1, ?)
                ON CONFLICT(address) DO UPDATE SET
                    nickname = COALESCE(excluded.nickname, tracked_wallets.nickname),
                    last_updated = excluded.last_updated,
                    metadata = excluded.metadata
            """, (
                address,
                nickname,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                str(metadata)
            ))

            imported += 1
            print(f"✅ {address[:10]}... ({nickname or 'unnamed'})")

        except Exception as e:
            skipped += 1
            print(f"❌ Skipped wallet: {e}")

    conn.commit()
    conn.close()

    return imported, skipped

def get_current_wallet_count():
    """Get current wallet count"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM tracked_wallets WHERE is_active = 1")
    count = cur.fetchone()[0]
    conn.close()
    return count

if __name__ == "__main__":
    print("🐋 NANSEN WALLET IMPORTER\n")

    if not NANSEN_API_KEY:
        print("❌ NASEN_API_KEY not found in .env")
        print("\nUsing fallback: Your 11 provided wallets + existing wallets")
        print(f"Current wallet count: {get_current_wallet_count()}")
        exit(1)

    print(f"Current wallet count: {get_current_wallet_count()}\n")

    print("Fetching wallets from Nansen...")
    wallets = fetch_nansen_wallets()

    if not wallets:
        print("\n⚠️ No wallets fetched from Nansen API")
        print("This might be due to:")
        print("1. API key permissions")
        print("2. Endpoint changes")
        print("3. Rate limiting")
        print(f"\nCurrent system has {get_current_wallet_count()} wallets")
        exit(0)

    print(f"\n📊 Total wallets fetched: {len(wallets)}")
    print("\nImporting to AURA database...")

    imported, skipped = import_wallets_to_aura(wallets)

    final_count = get_current_wallet_count()

    print(f"\n✅ IMPORT COMPLETE")
    print(f"   Imported: {imported}")
    print(f"   Skipped: {skipped}")
    print(f"   Total active wallets: {final_count}")
