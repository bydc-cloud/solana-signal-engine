#!/usr/bin/env python3
"""
REALITY MARKET ANALYZER
======================
Find what tokens are ACTUALLY moving with real volume RIGHT NOW.
No theoretical market caps - only current market reality.
"""

import requests
import time
import os
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

class RealityMarketAnalyzer:
    """Analyze actual current market conditions"""

    def __init__(self):
        self.birdeye_key = os.getenv('BIRDEYE_API_KEY')
        print(f"""
🔍 REALITY MARKET ANALYZER ACTIVE
================================
Finding tokens with ACTUAL movement RIGHT NOW
No theoretical filters - pure market reality analysis
        """)

    def get_current_market_movers(self) -> list:
        """Get tokens that are ACTUALLY moving with real volume right now"""
        all_movers = []

        if not self.birdeye_key:
            print("❌ No Birdeye API key available")
            return []

        # Multiple REALITY-based search strategies
        search_strategies = [
            ('Volume Leaders', {'sort_by': 'v24hUSD', 'sort_type': 'desc', 'limit': 50}),
            ('Price Gainers', {'sort_by': 'v24hChangePercent', 'sort_type': 'desc', 'limit': 50}),
            ('Most Active', {'sort_by': 'v24hUSD', 'sort_type': 'desc', 'limit': 50}),
        ]

        for strategy_name, params in search_strategies:
            try:
                print(f"🔍 Scanning: {strategy_name}...")

                url = "https://public-api.birdeye.so/defi/tokenlist"
                headers = {'X-API-KEY': self.birdeye_key}

                response = requests.get(url, headers=headers, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    tokens = data.get('data', {}).get('tokens', [])

                    for token in tokens:
                        if self.is_real_mover(token):
                            all_movers.append({
                                'symbol': token.get('symbol'),
                                'address': token.get('address'),
                                'price': token.get('price', 0),
                                'volume_24h': token.get('v24hUSD', 0),
                                'market_cap': token.get('mc', 0),
                                'price_change_24h': token.get('v24hChangePercent', 0),
                                'price_change_1h': 0,  # Not available in API
                                'unique_wallets': 0,  # Not available in API
                                'transactions_24h': 0,  # Not available in API
                                'liquidity': token.get('liquidity', 0),
                                'strategy': strategy_name,
                                'discovery_time': datetime.now().isoformat()
                            })

                    print(f"   Found {len([t for t in tokens if self.is_real_mover(t)])} real movers")
                else:
                    print(f"   ❌ API Error: {response.status_code}")

                time.sleep(0.5)  # Rate limiting

            except Exception as e:
                print(f"⚠️ Strategy {strategy_name} error: {e}")
                continue

        # Remove duplicates and sort by momentum score
        unique_movers = {}
        for mover in all_movers:
            address = mover['address']
            if address and address not in unique_movers:
                mover['momentum_score'] = self.calculate_momentum_score(mover)
                unique_movers[address] = mover

        final_movers = list(unique_movers.values())
        final_movers.sort(key=lambda x: x['momentum_score'], reverse=True)

        return final_movers

    def is_real_mover(self, token: dict) -> bool:
        """Check if token has REAL movement and isn't obviously fake"""
        try:
            volume_24h = token.get('v24hUSD', 0)
            market_cap = token.get('mc', 0)
            price_change_24h = abs(token.get('v24hChangePercent', 0))
            liquidity = token.get('liquidity', 0)
            symbol = token.get('symbol', '')

            # Skip stablecoins and wrapped tokens
            if symbol.upper() in ['USDC', 'USDT', 'SOL', 'WSOL', 'WETH', 'WBTC', 'DAI']:
                return False

            # REALITY CHECK: Must have actual activity
            if volume_24h < 10000:  # Minimum $10k volume
                return False

            if market_cap <= 0:  # Must have real market cap
                return False

            if market_cap < 5000:  # Too small
                return False

            if market_cap > 1000000000:  # Too big (over 1B)
                return False

            # Must show significant price movement OR very high volume relative to mcap
            volume_to_mcap = volume_24h / market_cap if market_cap > 0 else 0
            if price_change_24h < 10 and volume_to_mcap < 0.1:
                return False

            # Basic rug protection
            if liquidity > 0 and liquidity < 10000:  # Too low liquidity
                return False

            return True

        except Exception as e:
            return False

    def calculate_momentum_score(self, token: dict) -> float:
        """Calculate real momentum score based on actual activity"""
        try:
            volume_24h = token.get('volume_24h', 0)
            market_cap = token.get('market_cap', 0)
            price_change_24h = abs(token.get('price_change_24h', 0))
            liquidity = token.get('liquidity', 0)

            score = 0

            # Volume momentum (50% of score)
            if market_cap > 0:
                volume_ratio = volume_24h / market_cap
                if volume_ratio >= 2.0:
                    score += 50
                elif volume_ratio >= 1.0:
                    score += 40
                elif volume_ratio >= 0.5:
                    score += 30
                elif volume_ratio >= 0.2:
                    score += 20
                elif volume_ratio >= 0.1:
                    score += 10

            # Price momentum (30% of score)
            if price_change_24h >= 50:
                score += 30
            elif price_change_24h >= 20:
                score += 25
            elif price_change_24h >= 10:
                score += 15
            elif price_change_24h >= 5:
                score += 10

            # Liquidity factor (20% of score)
            if liquidity > 0 and market_cap > 0:
                liquidity_ratio = liquidity / market_cap
                if liquidity_ratio >= 0.5:
                    score += 20
                elif liquidity_ratio >= 0.2:
                    score += 15
                elif liquidity_ratio >= 0.1:
                    score += 10
                elif liquidity_ratio >= 0.05:
                    score += 5

            return min(score, 100)

        except Exception as e:
            return 0

    def analyze_market_reality(self):
        """Analyze current market reality and report findings"""
        print(f"\n🔍 SCANNING LIVE MARKET DATA...")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        movers = self.get_current_market_movers()

        if not movers:
            print("❌ No real movers found in current market")
            return

        print(f"\n🚀 REALITY ANALYSIS RESULTS:")
        print(f"📊 Total real movers found: {len(movers)}")

        # Analyze market cap distribution
        mcap_ranges = {
            'Under 10k': 0,
            '10k-100k': 0,
            '100k-1M': 0,
            '1M-10M': 0,
            '10M-100M': 0,
            'Over 100M': 0
        }

        for mover in movers:
            mcap = mover['market_cap']
            if mcap < 10000:
                mcap_ranges['Under 10k'] += 1
            elif mcap < 100000:
                mcap_ranges['10k-100k'] += 1
            elif mcap < 1000000:
                mcap_ranges['100k-1M'] += 1
            elif mcap < 10000000:
                mcap_ranges['1M-10M'] += 1
            elif mcap < 100000000:
                mcap_ranges['10M-100M'] += 1
            else:
                mcap_ranges['Over 100M'] += 1

        print(f"\n💰 MARKET CAP DISTRIBUTION (Real movers):")
        for range_name, count in mcap_ranges.items():
            percentage = (count / len(movers) * 100) if len(movers) > 0 else 0
            print(f"   {range_name}: {count} tokens ({percentage:.1f}%)")

        # Show top movers
        print(f"\n🔥 TOP 10 MOMENTUM TOKENS:")
        for i, mover in enumerate(movers[:10], 1):
            print(f"{i}. ${mover['symbol']}")
            print(f"   💎 Score: {mover['momentum_score']:.0f}/100")
            print(f"   📈 24h: {mover['price_change_24h']:+.1f}% | 1h: {mover['price_change_1h']:+.1f}%")
            print(f"   💸 Volume: ${mover['volume_24h']:,.0f} | MCap: ${mover['market_cap']:,.0f}")
            print(f"   👥 Wallets: {mover['unique_wallets']} | Source: {mover['strategy']}")
            print()

        # Identify best opportunities
        high_momentum = [m for m in movers if m['momentum_score'] >= 70]
        print(f"⚡ HIGH MOMENTUM OPPORTUNITIES: {len(high_momentum)} tokens (70+ score)")

        if high_momentum:
            print("🎯 READY FOR SIGNAL GENERATION!")
            return high_momentum
        else:
            print("⏳ Market in consolidation - will continue monitoring")
            return movers[:5]  # Return top 5 for analysis

if __name__ == "__main__":
    analyzer = RealityMarketAnalyzer()
    opportunities = analyzer.analyze_market_reality()

    print(f"\n✅ MARKET REALITY ANALYSIS COMPLETE")
    print(f"Found {len(opportunities) if opportunities else 0} actionable opportunities")