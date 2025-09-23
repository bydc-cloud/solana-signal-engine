#!/usr/bin/env python3
"""
MOMENTUM SIGNAL GENERATOR
========================
Generate actionable trading signals from real market momentum data.
Built on the working reality analyzer foundation.
"""

import requests
import time
import os
import json
from datetime import datetime
from pathlib import Path
import asyncio
import aiohttp

# Load environment
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

class MomentumSignalGenerator:
    """Generate trading signals from real momentum data"""

    def __init__(self):
        self.birdeye_key = os.getenv('BIRDEYE_API_KEY')
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat = os.getenv('TELEGRAM_CHAT_ID')

        print("""
🚀 MOMENTUM SIGNAL GENERATOR ACTIVE
==================================
Building on reality analyzer success
Generating actionable trading signals from real market data
        """)

    def get_market_movers(self) -> list:
        """Get current market movers using proven reality analyzer logic"""
        all_movers = []

        if not self.birdeye_key:
            print("❌ No Birdeye API key available")
            return []

        # Proven working search strategies
        search_strategies = [
            ('Volume Leaders', {'sort_by': 'v24hUSD', 'sort_type': 'desc', 'limit': 50}),
            ('Price Gainers', {'sort_by': 'v24hChangePercent', 'sort_type': 'desc', 'limit': 50}),
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
                        if self.is_signal_worthy(token):
                            signal_score = self.calculate_signal_score(token)
                            all_movers.append({
                                'symbol': token.get('symbol'),
                                'address': token.get('address'),
                                'price': token.get('price', 0),
                                'volume_24h': token.get('v24hUSD', 0),
                                'market_cap': token.get('mc', 0),
                                'price_change_24h': token.get('v24hChangePercent', 0),
                                'liquidity': token.get('liquidity', 0),
                                'signal_score': signal_score,
                                'strategy': strategy_name,
                                'discovery_time': datetime.now().isoformat(),
                                'jupiter_link': f"https://jup.ag/swap/SOL-{token.get('address', '')}"
                            })

                    qualifying = [t for t in tokens if self.is_signal_worthy(t)]
                    print(f"   Found {len(qualifying)} signal-worthy tokens")
                else:
                    print(f"   ❌ API Error: {response.status_code}")

                time.sleep(0.5)  # Rate limiting

            except Exception as e:
                print(f"⚠️ Strategy {strategy_name} error: {e}")
                continue

        # Remove duplicates and sort by signal score
        unique_movers = {}
        for mover in all_movers:
            address = mover['address']
            if address and address not in unique_movers:
                unique_movers[address] = mover

        final_movers = list(unique_movers.values())
        final_movers.sort(key=lambda x: x['signal_score'], reverse=True)

        return final_movers

    def is_signal_worthy(self, token: dict) -> bool:
        """Check if token meets signal generation criteria"""
        try:
            volume_24h = token.get('v24hUSD', 0)
            market_cap = token.get('mc', 0)
            price_change_24h = abs(token.get('v24hChangePercent', 0))
            liquidity = token.get('liquidity', 0)
            symbol = token.get('symbol', '')

            # Skip major tokens and stablecoins
            if symbol.upper() in ['USDC', 'USDT', 'SOL', 'WSOL', 'WETH', 'WBTC', 'DAI', 'BTC', 'ETH']:
                return False

            # Signal-worthy criteria (more aggressive than basic filtering)
            if volume_24h < 20000:  # Minimum $20k volume for signals
                return False

            if market_cap <= 0 or market_cap < 10000:  # Must have real market cap
                return False

            if market_cap > 500000000:  # Skip tokens over 500M (too established)
                return False

            # Must show significant movement OR exceptional volume
            volume_to_mcap = volume_24h / market_cap if market_cap > 0 else 0
            if price_change_24h < 15 and volume_to_mcap < 0.2:
                return False

            # Liquidity protection
            if liquidity > 0 and liquidity < 15000:
                return False

            return True

        except Exception as e:
            return False

    def calculate_signal_score(self, token: dict) -> float:
        """Calculate signal strength score (higher = stronger signal)"""
        try:
            volume_24h = token.get('v24hUSD', 0)
            market_cap = token.get('mc', 0)
            price_change_24h = abs(token.get('v24hChangePercent', 0))
            liquidity = token.get('liquidity', 0)

            score = 0

            # Volume momentum (40% weight)
            if market_cap > 0:
                volume_ratio = volume_24h / market_cap
                if volume_ratio >= 3.0:
                    score += 40
                elif volume_ratio >= 2.0:
                    score += 35
                elif volume_ratio >= 1.0:
                    score += 30
                elif volume_ratio >= 0.5:
                    score += 25
                elif volume_ratio >= 0.2:
                    score += 15

            # Price momentum (35% weight)
            if price_change_24h >= 100:
                score += 35
            elif price_change_24h >= 50:
                score += 30
            elif price_change_24h >= 25:
                score += 25
            elif price_change_24h >= 15:
                score += 20
            elif price_change_24h >= 10:
                score += 15

            # Liquidity/Safety factor (15% weight)
            if liquidity > 0 and market_cap > 0:
                liquidity_ratio = liquidity / market_cap
                if liquidity_ratio >= 0.3:
                    score += 15
                elif liquidity_ratio >= 0.1:
                    score += 10
                elif liquidity_ratio >= 0.05:
                    score += 5

            # Market cap sweet spot (10% weight)
            if 50000 <= market_cap <= 5000000:  # 50k to 5M sweet spot
                score += 10
            elif 10000 <= market_cap <= 50000000:  # 10k to 50M acceptable
                score += 5

            return min(score, 100)

        except Exception as e:
            return 0

    def filter_valid_signals(self, movers: list, min_score: int = 60) -> list:
        """Filter for high-quality signals only"""
        valid_signals = []

        for mover in movers:
            if mover['signal_score'] >= min_score:
                # Additional validation
                if self.validate_token_data(mover):
                    valid_signals.append(mover)

        return valid_signals

    def validate_token_data(self, token: dict) -> bool:
        """Final validation of token data quality"""
        try:
            # Check for obviously fake price movements
            price_change = token.get('price_change_24h', 0)
            if abs(price_change) > 10000000:  # Likely data error
                return False

            # Check for reasonable volume/mcap ratio
            volume = token.get('volume_24h', 0)
            mcap = token.get('market_cap', 0)
            if volume > mcap * 10:  # Volume > 10x mcap is suspicious
                return False

            # Must have valid address
            address = token.get('address', '')
            if not address or len(address) < 32:
                return False

            return True

        except Exception as e:
            return False

    async def send_signal_to_telegram(self, signal: dict):
        """Send trading signal to Telegram"""
        try:
            symbol = signal['symbol']
            score = signal['signal_score']
            price = signal['price']
            volume = signal['volume_24h']
            mcap = signal['market_cap']
            change = signal['price_change_24h']
            jupiter_link = signal['jupiter_link']

            # Format signal message
            score_emoji = "🔥" if score >= 80 else "⚡" if score >= 70 else "📈"
            change_emoji = "🚀" if change > 0 else "📉"

            message = f"""{score_emoji} <b>MOMENTUM SIGNAL DETECTED</b> {score_emoji}

💎 <b>Token:</b> ${symbol}
📊 <b>Signal Score:</b> {score}/100
💰 <b>Price:</b> ${price:.8f}
📈 <b>24h Change:</b> {change_emoji} {change:+.1f}%

💸 <b>Volume:</b> ${volume:,.0f}
🎯 <b>Market Cap:</b> ${mcap:,.0f}
💧 <b>Liquidity:</b> ${signal['liquidity']:,.0f}

🔗 <b>Trade Now:</b> <a href="{jupiter_link}">Jupiter Swap</a>

⏰ <b>Discovery:</b> {datetime.now().strftime('%H:%M:%S')}
🎯 <b>Source:</b> {signal['strategy']}

<b>🚀 REALITY-BASED MOMENTUM SCANNER 🚀</b>
<i>Actual signals from real market data</i>"""

            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': False
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data, timeout=15) as response:
                    if response.status == 200:
                        print(f"📤 Signal sent: ${symbol} (Score: {score})")
                        return True
                    else:
                        print(f"❌ Telegram error: HTTP {response.status}")

        except Exception as e:
            print(f"⚠️ Signal send error: {e}")

        return False

    async def generate_signals(self):
        """Main signal generation process"""
        print(f"\n🚀 GENERATING MOMENTUM SIGNALS...")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        movers = self.get_market_movers()

        if not movers:
            print("⚠️ No market movers found")
            return []

        # Filter for valid signals
        signals = self.filter_valid_signals(movers, min_score=70)

        if not signals:
            print(f"📊 Found {len(movers)} movers, but none met signal criteria (70+ score)")
            # Show top movers for analysis
            print("\n📈 TOP MOVERS (below signal threshold):")
            for i, mover in enumerate(movers[:5], 1):
                print(f"{i}. ${mover['symbol']}: {mover['signal_score']}/100 score")
            return []

        print(f"\n🎯 SIGNALS GENERATED: {len(signals)} high-quality opportunities")

        # Send signals to Telegram
        for signal in signals:
            await self.send_signal_to_telegram(signal)
            await asyncio.sleep(2)  # Rate limiting

        return signals

async def main():
    """Test signal generation"""
    try:
        generator = MomentumSignalGenerator()
        signals = await generator.generate_signals()

        if signals:
            print(f"\n✅ SUCCESS: Generated {len(signals)} trading signals!")
            print("🎯 Signals sent to Telegram for immediate action")
        else:
            print("\n⏳ No signals generated - market in low momentum phase")
            print("   Will continue monitoring for opportunities...")

    except KeyboardInterrupt:
        print("\n🛑 Signal generation stopped")
    except Exception as e:
        print(f"❌ Signal generation error: {e}")

if __name__ == "__main__":
    asyncio.run(main())