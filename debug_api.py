#!/usr/bin/env python3
"""Debug Birdeye API calls"""

import requests
import json
import os
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

def test_birdeye_api():
    birdeye_key = os.getenv('BIRDEYE_API_KEY')
    print(f"API Key: {birdeye_key[:10]}..." if birdeye_key else "No API key")

    if not birdeye_key:
        print("❌ No API key found")
        return

    # Test basic token list endpoint
    url = "https://public-api.birdeye.so/defi/tokenlist"
    headers = {'X-API-KEY': birdeye_key}

    # Test different parameter combinations
    test_cases = [
        {'sort_by': 'v24hUSD', 'sort_type': 'desc', 'limit': 10},
        {'sort_by': 'v24hUSD', 'sort_type': 'desc', 'limit': 100},
        {'sort_by': 'v24hChangePercent', 'sort_type': 'desc', 'limit': 100},
    ]

    print(f"Testing URL: {url}")
    print(f"Headers: {headers}")

    for i, params in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Params: {params}")

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print("✅ Success!")
                tokens = data.get('data', {}).get('tokens', [])
                print(f"Found {len(tokens)} tokens")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text[:200]}...")

        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_birdeye_api()