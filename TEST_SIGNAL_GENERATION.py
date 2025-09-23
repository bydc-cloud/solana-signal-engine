#!/usr/bin/env python3
"""
TEST SIGNAL GENERATION
=====================
Test if current thresholds generate any signals from real market data.
"""

import asyncio
import json
import time
import os
import aiohttp
import subprocess
from datetime import datetime, timedelta
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

class SignalGenerationTester:
    """Test signal generation with current thresholds"""

    def __init__(self):
        # Same thresholds as UPDATED production system
        self.SIGNAL_THRESHOLDS = {
            'min_volume_mcap_ratio': 2.0,    # Volume must be 2x market cap (more realistic)
            'max_market_cap': 10000000,      # Under $10M mcap (includes more legitimate tokens)
            'min_price_change': 5,           # 5%+ price increase (more realistic for current market)
            'max_price_change': 1000,        # Under 1000% (wider range)
            'min_confidence': 50             # 50+ confidence score (realistic threshold)
        }

        print(f"""
🧪 SIGNAL GENERATION TEST
=========================
Testing current production thresholds:
• Max Market Cap: ${self.SIGNAL_THRESHOLDS['max_market_cap']:,}
• Min Confidence: {self.SIGNAL_THRESHOLDS['min_confidence']}+
• Min Price Change: {self.SIGNAL_THRESHOLDS['min_price_change']}%
• Min Volume/MCap Ratio: {self.SIGNAL_THRESHOLDS['min_volume_mcap_ratio']}x
        """)

    def get_real_market_data(self) -> dict:
        """Get real market data from Birdeye API"""
        try:
            birdeye_key = os.getenv('BIRDEYE_API_KEY')
            if not birdeye_key:
                print("❌ No Birdeye API key found")
                return {'success': False, 'tokens': []}

            import requests
            url = "https://public-api.birdeye.so/defi/tokenlist"
            headers = {'X-API-KEY': birdeye_key}
            params = {'sort_by': 'v24hUSD', 'sort_type': 'desc', 'limit': 50}  # Test more tokens

            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                tokens = data.get('data', {}).get('tokens', [])

                live_tokens = []
                for i, token in enumerate(tokens):
                    if token.get('address') and token.get('symbol'):
                        live_tokens.append({
                            'symbol': token.get('symbol'),
                            'address': token.get('address'),
                            'price': f"${token.get('price', 0):.8f}",
                            'volume': f"${token.get('v24hUSD', 0):,.0f}",
                            'market_cap': f"${token.get('mc', 0):,.0f}",
                            'change_24h': f"{token.get('priceChange24hPercent', 0):+.1f}%",
                            'age': 'live',
                            'transactions': str(token.get('uniqueWallets24h', 0)),
                            'rank': i + 1
                        })

                print(f"✅ Got {len(live_tokens)} real tokens from Birdeye API")
                return {'success': True, 'tokens': live_tokens}

        except Exception as e:
            print(f"⚠️ Birdeye API error: {e}")
            return {'success': False, 'tokens': []}

    def parse_trading_number(self, text: str) -> float:
        """Parse numbers from trading data strings"""
        try:
            if not text or text == 'N/A':
                return 0.0

            # Clean the text
            clean_text = text.replace('$', '').replace('%', '').replace('+', '').replace('-', '').replace(',', '')

            # Handle multipliers
            multiplier = 1
            if 'K' in text.upper():
                multiplier = 1000
                clean_text = clean_text.replace('K', '').replace('k', '')
            elif 'M' in text.upper():
                multiplier = 1000000
                clean_text = clean_text.replace('M', '').replace('m', '')
            elif 'B' in text.upper():
                multiplier = 1000000000
                clean_text = clean_text.replace('B', '').replace('b', '')

            return float(clean_text) * multiplier
        except:
            return 0.0

    def calculate_signal_score(self, token_data: dict) -> dict:
        """Calculate signal score with detailed logging"""
        try:
            score = 0
            factors = []

            symbol = token_data.get('symbol', 'UNKNOWN')
            volume_str = token_data.get('volume', '$0')
            mcap_str = token_data.get('market_cap', '$0')
            change_str = token_data.get('change_24h', '0%')
            price = token_data.get('price', '$0')

            # Parse values
            volume = self.parse_trading_number(volume_str)
            market_cap = self.parse_trading_number(mcap_str)
            price_change = abs(self.parse_trading_number(change_str))
            price_value = self.parse_trading_number(price)

            print(f"\n📊 ANALYZING: ${symbol}")
            print(f"   Market Cap: ${market_cap:,.0f}")
            print(f"   Volume: ${volume:,.0f}")
            print(f"   Price Change: {price_change:.1f}%")
            print(f"   Price: {price}")

            # Check each threshold with UPDATED criteria
            meets_mcap = market_cap <= self.SIGNAL_THRESHOLDS['max_market_cap']
            meets_volume_ratio = (volume / market_cap if market_cap > 0 else 0) >= self.SIGNAL_THRESHOLDS['min_volume_mcap_ratio']
            meets_price_change = price_change >= self.SIGNAL_THRESHOLDS['min_price_change'] or price_change == 0  # Allow stable prices

            print(f"   ✅ MCap ≤ $10M: {meets_mcap} (${market_cap:,.0f})")
            print(f"   ✅ Vol/MCap ≥ 2x: {meets_volume_ratio} ({volume/market_cap if market_cap > 0 else 0:.1f}x)")
            print(f"   ✅ Price Change ≥ 5% (or stable): {meets_price_change} ({price_change:.1f}%)")

            # Calculate score - UPDATED more generous scoring
            if meets_mcap:
                score += 30
                factors.append(f"✅ Under $10M mcap: ${market_cap:,.0f}")
            else:
                score -= 10
                factors.append(f"❌ Over $10M mcap: ${market_cap:,.0f}")

            vol_ratio = volume / market_cap if market_cap > 0 else 0
            if vol_ratio >= 20:
                score += 25
                factors.append(f"🚀 Huge volume: {vol_ratio:.1f}x mcap")
            elif vol_ratio >= 5:
                score += 20
                factors.append(f"⚡ High volume: {vol_ratio:.1f}x mcap")
            elif vol_ratio >= 2:
                score += 15
                factors.append(f"✅ Good volume: {vol_ratio:.1f}x mcap")
            else:
                score += 5
                factors.append(f"📊 Low volume: {vol_ratio:.1f}x mcap")

            # Price scoring - more flexible
            if price_change >= 50:
                score += 20
                factors.append(f"🔥 Major pump: +{price_change:.1f}%")
            elif price_change >= 10:
                score += 15
                factors.append(f"📈 Good pump: +{price_change:.1f}%")
            elif price_change >= 5:
                score += 10
                factors.append(f"✅ Price increase: +{price_change:.1f}%")
            elif price_change == 0:
                score += 5
                factors.append(f"📊 Stable price (volume focus)")
            else:
                score -= 5
                factors.append(f"⚠️ Price decline: {price_change:.1f}%")

            print(f"   🎯 SCORE: {score}/100 (threshold: {self.SIGNAL_THRESHOLDS['min_confidence']})")

            return {
                'symbol': symbol,
                'score': score,
                'factors': factors,
                'volume': volume,
                'market_cap': market_cap,
                'price_change': price_change,
                'meets_threshold': score >= self.SIGNAL_THRESHOLDS['min_confidence'],
                'raw_data': token_data
            }

        except Exception as e:
            print(f"⚠️ Signal scoring error for {symbol}: {e}")
            return {'symbol': symbol, 'score': 0, 'factors': ['Scoring error']}

    def test_signal_generation(self):
        """Test if any tokens meet current signal thresholds"""
        print("\n🔍 EXTRACTING REAL MARKET DATA...")

        market_data = self.get_real_market_data()

        if not market_data.get('success', False):
            print("❌ Failed to get market data")
            return

        tokens = market_data.get('tokens', [])
        print(f"\n📊 ANALYZING {len(tokens)} TOKENS...")

        qualifying_signals = []
        all_signals = []

        for token in tokens:
            signal_data = self.calculate_signal_score(token)
            all_signals.append(signal_data)

            if signal_data['meets_threshold']:
                qualifying_signals.append(signal_data)

        # Results summary
        print(f"\n" + "="*60)
        print(f"🎯 SIGNAL GENERATION TEST RESULTS")
        print(f"="*60)
        print(f"📊 Total tokens analyzed: {len(tokens)}")
        print(f"🎯 Tokens meeting threshold: {len(qualifying_signals)}")
        print(f"📈 Signal generation rate: {len(qualifying_signals)/len(tokens)*100:.1f}%")

        if qualifying_signals:
            print(f"\n🔥 QUALIFYING SIGNALS:")
            for i, signal in enumerate(qualifying_signals[:5], 1):
                print(f"{i}. ${signal['symbol']} - {signal['score']}/100")
                for factor in signal['factors'][:3]:
                    print(f"   • {factor}")
        else:
            print(f"\n❌ NO SIGNALS MEET CURRENT THRESHOLDS!")
            print(f"\nTop scoring tokens that didn't qualify:")
            sorted_signals = sorted(all_signals, key=lambda x: x['score'], reverse=True)
            for i, signal in enumerate(sorted_signals[:5], 1):
                print(f"{i}. ${signal['symbol']} - {signal['score']}/100 (need {self.SIGNAL_THRESHOLDS['min_confidence']}+)")

        print(f"\n📊 THRESHOLD ANALYSIS:")
        mcap_fails = sum(1 for s in all_signals if s['market_cap'] > self.SIGNAL_THRESHOLDS['max_market_cap'])
        print(f"• Tokens over $2M mcap: {mcap_fails}/{len(tokens)} ({mcap_fails/len(tokens)*100:.1f}%)")

if __name__ == "__main__":
    tester = SignalGenerationTester()
    tester.test_signal_generation()