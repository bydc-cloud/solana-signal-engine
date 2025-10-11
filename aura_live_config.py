#!/usr/bin/env python3
"""
AURA Live System Configuration
Add wallets to track, configure CT (Crypto Twitter) monitoring, and manage live data sources
"""

import sqlite3
import logging
from datetime import datetime
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuraLiveConfig:
    """Configuration for AURA live system"""

    def __init__(self, db_path="aura.db"):
        self.db_path = db_path
        self._init_config_tables()

    def _init_config_tables(self):
        """Initialize configuration tables"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Whale wallets to track in real-time
        cur.execute("""
            CREATE TABLE IF NOT EXISTS live_whale_wallets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wallet_address TEXT UNIQUE NOT NULL,
                nickname TEXT,
                track_enabled INTEGER DEFAULT 1,
                alert_on_tx INTEGER DEFAULT 1,
                min_tx_value_usd REAL DEFAULT 10000,
                added_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_checked TEXT,
                total_alerts_sent INTEGER DEFAULT 0
            )
        """)

        # Crypto Twitter accounts to monitor
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ct_monitors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                twitter_handle TEXT UNIQUE NOT NULL,
                category TEXT,
                importance INTEGER DEFAULT 5,
                track_enabled INTEGER DEFAULT 1,
                alert_on_mention INTEGER DEFAULT 1,
                added_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_checked TEXT,
                total_mentions INTEGER DEFAULT 0
            )
        """)

        # Live data source configuration
        cur.execute("""
            CREATE TABLE IF NOT EXISTS live_data_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name TEXT UNIQUE NOT NULL,
                source_type TEXT,
                api_endpoint TEXT,
                enabled INTEGER DEFAULT 1,
                rate_limit_per_min INTEGER,
                last_used TEXT,
                total_requests INTEGER DEFAULT 0,
                total_errors INTEGER DEFAULT 0
            )
        """)

        conn.commit()
        conn.close()

        logger.info("✅ Configuration tables initialized")

    def add_whale_wallet(self, address: str, nickname: str = None, min_tx_value: float = 10000) -> bool:
        """Add a whale wallet to track"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO live_whale_wallets (wallet_address, nickname, min_tx_value_usd)
                VALUES (?, ?, ?)
            """, (address, nickname, min_tx_value))

            conn.commit()
            conn.close()

            logger.info(f"✅ Added whale wallet: {nickname or address[:8]}...")
            return True

        except sqlite3.IntegrityError:
            logger.warning(f"⚠️  Wallet {address} already tracked")
            return False
        except Exception as e:
            logger.error(f"❌ Error adding wallet: {e}")
            return False

    def add_ct_monitor(self, twitter_handle: str, category: str = "general", importance: int = 5) -> bool:
        """Add a Crypto Twitter account to monitor"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()

            # Remove @ if present
            handle = twitter_handle.lstrip('@')

            cur.execute("""
                INSERT INTO ct_monitors (twitter_handle, category, importance)
                VALUES (?, ?, ?)
            """, (handle, category, importance))

            conn.commit()
            conn.close()

            logger.info(f"✅ Added CT monitor: @{handle} ({category}, importance: {importance}/10)")
            return True

        except sqlite3.IntegrityError:
            logger.warning(f"⚠️  @{twitter_handle} already monitored")
            return False
        except Exception as e:
            logger.error(f"❌ Error adding CT monitor: {e}")
            return False

    def get_tracked_wallets(self) -> List[Dict]:
        """Get all tracked whale wallets"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            SELECT wallet_address, nickname, track_enabled, min_tx_value_usd, added_at, total_alerts_sent
            FROM live_whale_wallets
            WHERE track_enabled = 1
            ORDER BY total_alerts_sent DESC
        """)

        wallets = []
        for row in cur.fetchall():
            wallets.append({
                "address": row[0],
                "nickname": row[1] or row[0][:8] + "...",
                "enabled": bool(row[2]),
                "min_tx_value": row[3],
                "added_at": row[4],
                "total_alerts": row[5]
            })

        conn.close()
        return wallets

    def get_ct_monitors(self) -> List[Dict]:
        """Get all CT monitors"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            SELECT twitter_handle, category, importance, track_enabled, added_at, total_mentions
            FROM ct_monitors
            WHERE track_enabled = 1
            ORDER BY importance DESC, total_mentions DESC
        """)

        monitors = []
        for row in cur.fetchall():
            monitors.append({
                "handle": f"@{row[0]}",
                "category": row[1],
                "importance": row[2],
                "enabled": bool(row[3]),
                "added_at": row[4],
                "total_mentions": row[5]
            })

        conn.close()
        return monitors

    def remove_whale_wallet(self, address: str) -> bool:
        """Remove a whale wallet from tracking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()

            cur.execute("DELETE FROM live_whale_wallets WHERE wallet_address = ?", (address,))

            conn.commit()
            affected = cur.rowcount
            conn.close()

            if affected > 0:
                logger.info(f"✅ Removed whale wallet: {address[:8]}...")
                return True
            else:
                logger.warning(f"⚠️  Wallet {address} not found")
                return False

        except Exception as e:
            logger.error(f"❌ Error removing wallet: {e}")
            return False

    def remove_ct_monitor(self, twitter_handle: str) -> bool:
        """Remove a CT monitor"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()

            handle = twitter_handle.lstrip('@')
            cur.execute("DELETE FROM ct_monitors WHERE twitter_handle = ?", (handle,))

            conn.commit()
            affected = cur.rowcount
            conn.close()

            if affected > 0:
                logger.info(f"✅ Removed CT monitor: @{handle}")
                return True
            else:
                logger.warning(f"⚠️  @{twitter_handle} not found")
                return False

        except Exception as e:
            logger.error(f"❌ Error removing CT monitor: {e}")
            return False

    def get_configuration_summary(self) -> Dict:
        """Get summary of current configuration"""
        wallets = self.get_tracked_wallets()
        ct_monitors = self.get_ct_monitors()

        return {
            "whale_wallets": {
                "total": len(wallets),
                "wallets": wallets
            },
            "ct_monitors": {
                "total": len(ct_monitors),
                "monitors": ct_monitors
            },
            "timestamp": datetime.now().isoformat()
        }


# CLI for managing configuration
def main():
    """Interactive configuration manager"""
    import sys

    config = AuraLiveConfig()

    if len(sys.argv) < 2:
        print("🔧 AURA Live Configuration Manager")
        print("=" * 50)
        print()
        print("Usage:")
        print("  python aura_live_config.py add-wallet <address> [nickname] [min_value]")
        print("  python aura_live_config.py add-ct <handle> [category] [importance]")
        print("  python aura_live_config.py list-wallets")
        print("  python aura_live_config.py list-ct")
        print("  python aura_live_config.py remove-wallet <address>")
        print("  python aura_live_config.py remove-ct <handle>")
        print("  python aura_live_config.py summary")
        print()
        return

    command = sys.argv[1]

    if command == "add-wallet":
        if len(sys.argv) < 3:
            print("❌ Error: Wallet address required")
            return

        address = sys.argv[2]
        nickname = sys.argv[3] if len(sys.argv) > 3 else None
        min_value = float(sys.argv[4]) if len(sys.argv) > 4 else 10000

        config.add_whale_wallet(address, nickname, min_value)

    elif command == "add-ct":
        if len(sys.argv) < 3:
            print("❌ Error: Twitter handle required")
            return

        handle = sys.argv[2]
        category = sys.argv[3] if len(sys.argv) > 3 else "general"
        importance = int(sys.argv[4]) if len(sys.argv) > 4 else 5

        config.add_ct_monitor(handle, category, importance)

    elif command == "list-wallets":
        wallets = config.get_tracked_wallets()
        print(f"\n🐋 Tracked Whale Wallets ({len(wallets)} total):")
        print("=" * 70)
        for w in wallets:
            print(f"  {w['nickname']:<20} | ${w['min_tx_value']:>10,.0f} min | {w['total_alerts']} alerts")

    elif command == "list-ct":
        monitors = config.get_ct_monitors()
        print(f"\n📱 CT Monitors ({len(monitors)} total):")
        print("=" * 70)
        for m in monitors:
            print(f"  {m['handle']:<20} | {m['category']:<15} | Importance: {m['importance']}/10")

    elif command == "remove-wallet":
        if len(sys.argv) < 3:
            print("❌ Error: Wallet address required")
            return
        config.remove_whale_wallet(sys.argv[2])

    elif command == "remove-ct":
        if len(sys.argv) < 3:
            print("❌ Error: Twitter handle required")
            return
        config.remove_ct_monitor(sys.argv[2])

    elif command == "summary":
        summary = config.get_configuration_summary()
        print("\n📊 AURA Live Configuration Summary")
        print("=" * 50)
        print(f"  Whale Wallets: {summary['whale_wallets']['total']}")
        print(f"  CT Monitors: {summary['ct_monitors']['total']}")
        print(f"  Last Updated: {summary['timestamp']}")

    else:
        print(f"❌ Unknown command: {command}")


if __name__ == "__main__":
    main()
