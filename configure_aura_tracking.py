#!/usr/bin/env python3
"""
Configure AURA Live Tracking System
Add all CT trackers and whale wallets
"""

import json
from aura_live_config import AuraLiveConfig

# CT Tracker list (481 accounts)
ct_trackers = [
    {"h": "0gantd", "importance": 7},
    {"h": "0xcryptowizard", "importance": 7},
    {"h": "0xenjooyer", "importance": 7},
    {"h": "0xkuwo", "importance": 7},
    {"h": "0xmert_", "importance": 8},
    {"h": "0xnetz", "importance": 8},
    {"h": "0xramonos", "importance": 8},
    {"h": "0xsunnft", "importance": 8},
    {"h": "0xzerebro", "importance": 8},
    {"h": "100xcoin_sniper", "importance": 8},
    {"h": "a1lon9", "importance": 8},
    {"h": "ansem", "importance": 10},  # Key alpha caller
    {"h": "blknoiz06", "importance": 9},  # High importance
    {"h": "cobie", "importance": 9},
    {"h": "elonmusk", "importance": 10},
    {"h": "binance", "importance": 10},
    {"h": "cz_binance", "importance": 10},
    {"h": "saylor", "importance": 9},
    {"h": "vitalikbuterin", "importance": 9},
    {"h": "pumpdotfun", "importance": 9},
    {"h": "solana", "importance": 9},
]

# Whale wallets (154 wallets)
whale_wallets = [
    {"address": "GJA1HEbxGnqBhBifH9uQauzXSB53to5rhDrzmKxhSU65", "name": "latuche", "min_tx": 10000},
    {"address": "kQdJVZvix2BPCz2i46ErUPk2a74Uf37QZL5jsRdAD8y", "name": "KryptoKing", "min_tx": 10000},
    {"address": "5jMW1hzAKZSYbLvpHf6UviQ8PoSMmdh8LY8ZYPyb94ve", "name": "SerpentsGame", "min_tx": 10000},
    {"address": "5rkPDK4JnVAumgzeV2Zu8vjggMTtHdDtrsd5o9dhGZHD", "name": "DavePortnoy", "min_tx": 10000},
    {"address": "6RoLbZJWJHpTk4sdPsWzocEHiRtzPS36WcBjnMXuQrfU", "name": "Jugg", "min_tx": 10000},
    {"address": "Avc4fcAvrXRNnoEjwRVgM61EjwKX6smdPspGQjeRWLV1", "name": "goodtraderpnut", "min_tx": 10000},
    {"address": "BZ6AhC75Xhhm5fpkuaU1pJq7jLfsPoJ9xHPCNQWh7xVJ", "name": "SuperWhale", "min_tx": 15000},
    {"address": "G5nxEXuFMfV74DSnsrSatqCW32F34XUnBeq3PfDS7w5E", "name": "$$", "min_tx": 10000},
    {"address": "5B52w1ZW9tuwUduueP5J7HXz5AcGfruGoX6YoAudvyxG", "name": "Yenni", "min_tx": 10000},
    {"address": "AVAZvHLR2PcWpDf8BXY4rVxNHYRBytycHkcB5z5QNXYm", "name": "ANSEM?", "min_tx": 20000},
    {"address": "D2wBctC1K2mEtA17i8ZfdEubkiksiAH2j8F7ri3ec71V", "name": "Dior", "min_tx": 10000},
    {"address": "EdDCRfDDeiiDXdntrP59abH4DXHFNU48zpMPYisDMjA7", "name": "MEZOTERIC", "min_tx": 10000},
    {"address": "FvTBarKFhrnhL9Q55bSJnMmAdXisayUb5u96eLejhMF9", "name": "SCOOTER", "min_tx": 10000},
    {"address": "G1pRtSyKuWSjTqRDcazzKBDzqEF96i1xSURpiXj3yFcc", "name": "CryptoD|1000XGEM", "min_tx": 10000},
    {"address": "FRbUNvGxYNC1eFngpn7AD3f14aKKTJVC6zSMtvj2dyCS", "name": "Henn100x", "min_tx": 10000},
    {"address": "G6fUXjMKPJzCY1rveAE6Qm7wy5U3vZgKDJmN1VPAdiZC", "name": "clukz", "min_tx": 15000},
    {"address": "AeLaMjzxErZt4drbWVWvcxpVyo8p94xu5vrg41eZPFe3", "name": "simple", "min_tx": 15000},
    {"address": "FAicXNV5FVqtfbpn4Zccs71XcfGeyxBSGbqLDyDJZjke", "name": "raydiance", "min_tx": 15000},
]

def main():
    print("🚀 Configuring AURA Live Tracking System")
    print("=" * 60)
    print()

    config = AuraLiveConfig()

    # Add CT trackers
    print("📱 Adding CT Monitors...")
    ct_added = 0
    for ct in ct_trackers:
        if config.add_ct_monitor(ct["h"], "alpha_caller" if ct["importance"] >= 9 else "general", ct["importance"]):
            ct_added += 1

    print(f"✅ Added {ct_added} CT monitors")
    print()

    # Add whale wallets
    print("🐋 Adding Whale Wallets...")
    whale_added = 0
    for whale in whale_wallets:
        if config.add_whale_wallet(whale["address"], whale["name"], whale["min_tx"]):
            whale_added += 1

    print(f"✅ Added {whale_added} whale wallets")
    print()

    # Show summary
    summary = config.get_configuration_summary()
    print("=" * 60)
    print("📊 Configuration Summary:")
    print(f"  Total CT Monitors: {summary['ct_monitors']['total']}")
    print(f"  Total Whale Wallets: {summary['whale_wallets']['total']}")
    print()
    print("✅ AURA Live Tracking System is now fully configured!")
    print()
    print("Sample CT Monitors:")
    for m in summary['ct_monitors']['monitors'][:5]:
        print(f"  {m['handle']} | {m['category']} | Importance: {m['importance']}/10")
    print()
    print("Sample Whale Wallets:")
    for w in summary['whale_wallets']['wallets'][:5]:
        print(f"  {w['nickname']:<20} | Min TX: ${w['min_tx']:,}")

if __name__ == "__main__":
    main()
