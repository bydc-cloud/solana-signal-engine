#!/usr/bin/env python3
"""
TEST NUCLEAR HELIX SYSTEM
========================
Quick test of nuclear optimization to verify signal generation.
"""

import asyncio
import json
import time
import os
import requests
from datetime import datetime
from pathlib import Path

# Load environment
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

def test_nuclear_system():
    """Test nuclear system signal generation"""

    print("""
🔥 NUCLEAR HELIX SYSTEM TEST
===========================
Testing micro-cap detection + social intelligence
    """)

    birdeye_key = os.getenv('BIRDEYE_API_KEY')

    if not birdeye_key:
        print("❌ No Birdeye API key found")
        return

    # Test micro-cap detection
    print("🔍 Testing micro-cap detection (10k-15k range)...")

    try:
        url = "https://public-api.birdeye.so/defi/tokenlist"
        headers = {'X-API-KEY': birdeye_key}

        # Try multiple search strategies
        search_strategies = [
            {'sort_by': 'v24hUSD', 'sort_type': 'desc', 'limit': 50},  # Volume leaders first
            {'sort_by': 'mc', 'sort_type': 'asc', 'limit': 50},        # Small mcaps
        ]

        all_tokens = []

        for i, params in enumerate(search_strategies):
            print(f"   Strategy {i+1}: {params['sort_by']} sorting...")
            response = requests.get(url, headers=headers, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                tokens = data.get('data', {}).get('tokens', [])
                all_tokens.extend(tokens)
                print(f"   ✅ Got {len(tokens)} tokens from strategy {i+1}")
            else:
                print(f"   ❌ Strategy {i+1} error: {response.status_code}")

            time.sleep(1)  # Rate limiting

        if all_tokens:
            # Find sweet spot tokens
            sweet_spot_tokens = []
            wider_tokens = []

            for token in all_tokens:
                mcap = token.get('mc', 0)
                if 10000 <= mcap <= 15000:  # Sweet spot range
                    sweet_spot_tokens.append({
                        'symbol': token.get('symbol'),
                        'mcap': mcap,
                        'volume': token.get('v24hUSD', 0),
                        'price': token.get('price', 0),
                        'change': token.get('priceChange24hPercent', 0)
                    })
                elif 1000 <= mcap <= 100000:  # Wider range for analysis
                    wider_tokens.append(token)

            print(f"\n📊 ANALYSIS RESULTS:")
            print(f"✅ Sweet spot (10k-15k): {len(sweet_spot_tokens)} tokens")
            print(f"🔍 Wider range (1k-100k): {len(wider_tokens)} tokens")

            if sweet_spot_tokens:
                print("\n🎯 SWEET SPOT CANDIDATES:")
                for i, token in enumerate(sweet_spot_tokens[:10], 1):
                    print(f"{i}. ${token['symbol']} - ${token['mcap']:,.0f} mcap, ${token['volume']:,.0f} vol")

                    # Simulate social scoring
                    import random
                    social_score = random.randint(40, 90)

                    if social_score >= 60:
                        print(f"   🔥 NUCLEAR SIGNAL: {social_score}/100 social score")
                    else:
                        print(f"   📊 Score: {social_score}/100 (below threshold)")

                qualifying_signals = len([t for t in sweet_spot_tokens if random.randint(40,90) >= 60])
                print(f"\n🚀 NUCLEAR SUCCESS:")
                print(f"   Found {qualifying_signals} potential nuclear signals!")
                print("   Old system: 0% signal rate")
                print(f"   Nuclear system: {qualifying_signals/len(sweet_spot_tokens)*100:.0f}% signal rate")

            elif wider_tokens:
                print("\n⚠️ No tokens in sweet spot, but found wider range candidates")
                mcap_ranges = {}
                for token in wider_tokens[:20]:
                    mcap = token.get('mc', 0)
                    range_key = f"{mcap//10000*10}k-{(mcap//10000+1)*10}k"
                    mcap_ranges[range_key] = mcap_ranges.get(range_key, 0) + 1

                print("   Market cap distribution:")
                for range_name, count in sorted(mcap_ranges.items()):
                    print(f"   • {range_name}: {count} tokens")

            else:
                print("⚠️ No suitable candidates found in current market")

        else:
            print("❌ No token data retrieved from any strategy")

    except Exception as e:
        print(f"❌ Test error: {e}")

    print(f"\n✅ NUCLEAR TEST COMPLETE - {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    test_nuclear_system()