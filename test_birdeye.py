#!/usr/bin/env python3
import requests
import os
import time

# Load API key
api_key = "21c8998710ad4def9b1d406981e999ea"

# Test each strategy
strategies = [
    ("High Volume", {'sort_by': 'v24hUSD', 'sort_type': 'desc', 'limit': 50}),
    ("Top Gainers", {'sort_by': 'v24hChangePercent', 'sort_type': 'desc', 'limit': 50}),
    ("Deep Liquidity", {'sort_by': 'liquidity', 'sort_type': 'desc', 'limit': 50}),
    ("Micro Caps", {'sort_by': 'mc', 'sort_type': 'asc', 'limit': 50}),
]

url = "https://public-api.birdeye.so/defi/tokenlist"
headers = {
    'X-API-KEY': api_key,
    'x-chain': 'solana',
}

for strategy_name, params in strategies:
    query = dict(params)
    query.setdefault('chain', 'solana')

    print(f"Testing {strategy_name}...")
    start_time = time.time()

    try:
        response = requests.get(url, headers=headers, params=query, timeout=8)
        elapsed = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            token_count = len(data.get('data', {}).get('tokens', []))
            print(f"✅ {strategy_name}: {token_count} tokens in {elapsed:.2f}s")
        else:
            print(f"❌ {strategy_name}: HTTP {response.status_code} in {elapsed:.2f}s")
            print(f"   Response: {response.text[:100]}")

    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"⏰ {strategy_name}: Timeout after {elapsed:.2f}s")
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"💥 {strategy_name}: Error in {elapsed:.2f}s - {e}")

    time.sleep(1)  # Rate limiting

print("Test complete!")