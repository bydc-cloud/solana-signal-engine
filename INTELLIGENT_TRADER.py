#!/usr/bin/env python3
"""
INTELLIGENT HELIX TRADER - WHALE-BACKED MOONSHOT SIGNALS
========================================================
Enhanced trader that uses intelligence database from DATA_COLLECTOR
for rapid-fire whale-backed signals with confidence scoring.
"""

import asyncio
import aiohttp
import json
import os
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Load environment
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

class IntelligentTrader:
    """Intelligent trader using whale intelligence and moonshot patterns"""

    def __init__(self):
        self.birdeye_key = os.getenv('BIRDEYE_API_KEY')
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat = os.getenv('TELEGRAM_CHAT_ID')

        if not all([self.birdeye_key, self.telegram_token, self.telegram_chat]):
            raise ValueError("Missing required API keys")

        # Intelligence database paths
        self.data_dir = Path(__file__).parent / "data"
        self.all_tokens_file = self.data_dir / "all_tokens.json"
        self.whale_wallets_file = self.data_dir / "whale_wallets.json"
        self.moonshot_history_file = self.data_dir / "moonshot_history.json"

        # Initialize intelligence cache (loaded once, cached for speed)
        self.intelligence_db = {}
        self.moonshot_patterns = []
        self.last_signals = []  # Prevent spam
        self.fresh_tokens_file = self.data_dir / "fresh_tokens.json"
        self.intelligence_loaded = False

        print("🧠 Intelligent Trader initializing...")
        self.load_intelligence_database_once()

    def load_intelligence_database_once(self):
        """Load intelligence from DATA_COLLECTOR files ONCE for speed"""
        try:
            # Load token intelligence
            if self.all_tokens_file.exists():
                with open(self.all_tokens_file, 'r') as f:
                    self.intelligence_db = json.load(f)
                print(f"✅ Loaded intelligence for {len(self.intelligence_db)} tokens")

            # Load moonshot patterns
            if self.moonshot_history_file.exists():
                with open(self.moonshot_history_file, 'r') as f:
                    self.moonshot_patterns = json.load(f)
                print(f"✅ Loaded {len(self.moonshot_patterns)} moonshot patterns")

            if not self.intelligence_db:
                print("⚠️ No intelligence database found - run DATA_COLLECTOR.py first")

            self.intelligence_loaded = True

        except Exception as e:
            print(f"⚠️ Intelligence loading error: {e}")

    def refresh_intelligence_periodically(self):
        """Refresh intelligence database every 5 minutes for updated whale data"""
        try:
            if self.all_tokens_file.exists():
                with open(self.all_tokens_file, 'r') as f:
                    self.intelligence_db = json.load(f)

            if self.moonshot_history_file.exists():
                with open(self.moonshot_history_file, 'r') as f:
                    self.moonshot_patterns = json.load(f)

        except Exception as e:
            print(f"⚠️ Intelligence refresh error: {e}")

    async def send_telegram(self, message):
        """Send Telegram notification"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': False
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    return response.status == 200
        except:
            return False

    def get_fresh_tokens_from_collector(self) -> List[Dict]:
        """Get fresh token data from DATA_COLLECTOR (no API calls)"""
        try:
            if not self.fresh_tokens_file.exists():
                return []

            with open(self.fresh_tokens_file, 'r') as f:
                fresh_data = json.load(f)

            # Check if data is fresh (within last 5 minutes)
            timestamp_str = fresh_data.get('timestamp', '')
            if timestamp_str:
                data_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                age = datetime.now() - data_time.replace(tzinfo=None)

                if age.total_seconds() > 300:  # 5 minutes old
                    print("⚠️ Fresh token data is stale - waiting for DATA_COLLECTOR")
                    return []

            tokens = fresh_data.get('tokens', [])
            print(f"✅ Retrieved {len(tokens)} fresh tokens from DATA_COLLECTOR")
            return tokens

        except Exception as e:
            print(f"⚠️ Error reading fresh tokens: {e}")
            return []

    def calculate_intelligence_score(self, token: Dict) -> Dict[str, Any]:
        """Calculate intelligence score based on multiple factors - OPTIMIZED FOR SPEED"""
        address = token.get('address', '')
        symbol = token.get('symbol', 'Unknown')

        try:
            price_change_24h = float(token.get('priceChange24hPercent') or 0)
            volume_24h = float(token.get('v24hUSD') or 0)
            market_cap = float(token.get('mc') or 0)
        except (ValueError, TypeError):
            return {'score': 0, 'factors': []}

        factors = []
        score = 0

        # REAL MONEY PRINTER FILTERS - UNCOMFORTABLE EARLY ENTRIES

        # ANTI-RUG PROTECTION (Essential but not over-restrictive)
        if market_cap < 40000:  # Below $40k = definite rug territory
            return {'score': 0, 'factors': ['🚨 BLOCKED: Market cap too low (rug risk)']}

        if market_cap > 400000:  # Above $400k = slower moonshot potential
            return {'score': 0, 'factors': ['🚨 BLOCKED: Market cap too high for maximum gains']}

        # MINIMUM WHALE INTEREST (Real but achievable)
        if volume_24h < 800000:  # Below $800k = insufficient interest
            return {'score': 0, 'factors': ['🚨 BLOCKED: Volume below whale threshold']}

        # REAL WHALE TERRITORY (Messy but profitable)
        vol_mcap_ratio = volume_24h / market_cap if market_cap > 0 else 0
        if vol_mcap_ratio < 2.0:  # Too low = no real interest
            return {'score': 0, 'factors': ['🚨 BLOCKED: Volume/MCap too low - no activity']}
        if vol_mcap_ratio > 35.0:  # Truly impossible = fake volume
            return {'score': 0, 'factors': ['🚨 BLOCKED: Volume/MCap impossible - fake volume']}

        # EARLY ENTRY TIMING (Uncomfortable but profitable zone)
        if price_change_24h < 3.0:  # Too early = no momentum yet
            return {'score': 0, 'factors': ['🚨 BLOCKED: No momentum detected yet']}
        if price_change_24h > 25.0:  # Too late = missed early entry
            return {'score': 0, 'factors': ['🚨 BLOCKED: Entry too late - momentum started']}

        # BASIC RUG DETECTION (Block obvious fakes)
        if abs(price_change_24h) < 0.5:  # Near 0% = suspicious
            return {'score': 0, 'factors': ['🚨 BLOCKED: Suspicious price pattern']}

        # VOLUME SPIKE DETECTION (Must show real activity)
        if vol_mcap_ratio < 5.0 and price_change_24h > 15.0:  # Price up but no volume = fake
            return {'score': 0, 'factors': ['🚨 BLOCKED: Price pump without volume support']}

        # NUCLEAR FACTOR 3: Volume Anomaly Detection (0-40 points)
        # Find ACCUMULATION PHASE - massive volume with small price moves
        volume_to_mcap_ratio = volume_24h / max(market_cap, 1) if market_cap > 0 else 0

        if volume_24h > 2000000 and price_change_24h < 10:  # Massive volume, small pump
            if volume_to_mcap_ratio > 2.0:  # Volume > 2x market cap
                score += 40
                factors.append(f"🚨 STEALTH ACCUMULATION: ${volume_24h:,.0f} volume, only +{price_change_24h:.1f}%")
            elif volume_to_mcap_ratio > 1.0:
                score += 30
                factors.append(f"🐋 WHALE LOADING: Volume/MCap ratio {volume_to_mcap_ratio:.1f}x")
        elif volume_24h > 1000000 and price_change_24h < 5:  # High volume, flat price
            score += 25
            factors.append(f"📈 PRE-PUMP PATTERN: ${volume_24h:,.0f} volume, +{price_change_24h:.1f}%")
        elif price_change_24h > 50:  # Traditional pump (lower priority now)
            score += 15
            factors.append(f"Late pump: +{price_change_24h:.1f}%")

        # NUCLEAR FACTOR 2: Stealth Whale Pattern (0-35 points)
        # Low market cap + massive volume = whale accumulation
        if market_cap < 500000 and volume_24h > 2000000:  # Sub-500k mcap, whale volume
            score += 35
            factors.append(f"🎯 MOONSHOT SETUP: ${market_cap:,.0f} mcap, ${volume_24h:,.0f} volume")
        elif market_cap < 1000000 and volume_24h > 5000000:  # Sub-1M mcap, ultra whale volume
            score += 30
            factors.append(f"🚀 ULTRA WHALE TARGET: ${market_cap:,.0f} mcap, ${volume_24h:,.0f} volume")
        elif 50000 < market_cap < 200000 and volume_24h > 1000000:  # Micro cap, good volume
            score += 25
            factors.append(f"💎 HIDDEN GEM: ${market_cap:,.0f} mcap, ${volume_24h:,.0f} volume")

        # NUCLEAR FACTOR 3: Nuclear Market Cap Filter (0-20 points)
        if 50000 < market_cap < 500000:  # Nuclear moonshot zone
            score += 20
            factors.append(f"🔥 NUCLEAR ZONE: ${market_cap:,.0f} mcap")
        elif 10000 < market_cap < 50000:  # Ultra micro (high risk/reward)
            score += 15
            factors.append(f"⚡ MICRO CAP: ${market_cap:,.0f} mcap")
        elif market_cap > 10000000:  # Too big for moonshots
            score -= 10
            factors.append(f"⚠️ Large cap: ${market_cap:,.0f}")

        # Factor 4: Intelligence database bonus (0-25 points)
        if address in self.intelligence_db:
            intelligence = self.intelligence_db[address]
            last_scan = intelligence.get('last_scan', '')

            # Recent whale activity bonus
            if last_scan:
                try:
                    scan_time = datetime.fromisoformat(last_scan.replace('Z', '+00:00'))
                    if datetime.now() - scan_time < timedelta(hours=1):
                        score += 15
                        factors.append("Recent whale scan")
                except:
                    pass

            # Historical performance bonus
            hist_change = intelligence.get('price_change_24h', 0)
            if hist_change > 50:
                score += 10
                factors.append("Historical performer")

        # NUCLEAR FACTOR 5: Breakout Setup Detection (0-20 points)
        # Detect tokens preparing for massive breakouts
        if 100000 < market_cap < 2000000:  # Optimal breakout range
            volume_mcap_ratio = volume_24h / market_cap
            if volume_mcap_ratio > 3.0:  # Volume 3x larger than mcap
                if 5 < price_change_24h < 50:  # Controlled pump phase
                    score += 20
                    factors.append(f"🚀 BREAKOUT SETUP: Volume {volume_mcap_ratio:.1f}x mcap, controlled pump")
                elif price_change_24h < 5:  # Silent accumulation
                    score += 15
                    factors.append(f"⚡ PRE-BREAKOUT: Volume {volume_mcap_ratio:.1f}x mcap, silent loading")

        # Factor 6: Moonshot pattern matching (0-bonus points)
        moonshot_bonus = self.check_moonshot_patterns(symbol, price_change_24h, volume_24h, market_cap)
        score += moonshot_bonus
        if moonshot_bonus > 0:
            factors.append(f"Moonshot pattern: +{moonshot_bonus}")

        # NUCLEAR FACTOR 7: Ultimate ROI Filter (bonus/penalty points)
        # Penalize tokens that are too late in pump cycle
        if price_change_24h > 300:  # Already 3x+ pumped
            score -= 25
            factors.append(f"⚠️ LATE PUMP: Already +{price_change_24h:.1f}% - reduced score")
        elif price_change_24h > 500:  # Extreme pump - likely too late
            score -= 40
            factors.append(f"❌ EXTREME LATE: +{price_change_24h:.1f}% - avoid")

        # Ultra bonus for perfect nuclear conditions
        if (volume_24h > 3000000 and market_cap < 500000 and
            price_change_24h < 20 and volume_24h > market_cap * 5):
            score += 25
            factors.append(f"💎 NUCLEAR PERFECT: Ultra whale + micro cap + early stage")

        return {
            'score': min(score, 100),  # Cap at 100
            'factors': factors,
            'price_change': price_change_24h,
            'volume': volume_24h,
            'market_cap': market_cap
        }

    def check_moonshot_patterns(self, symbol: str, price_change: float, volume: float, market_cap: float) -> int:
        """Check if token matches historical moonshot patterns"""
        bonus = 0

        # Pattern 1: Historical moonshot signature
        for pattern in self.moonshot_patterns:
            try:
                pattern_volume = pattern.get('volume_signature', 0)
                pattern_pump = pattern.get('pump_magnitude', 0)

                # Volume similarity
                if abs(volume - pattern_volume) / max(pattern_volume, 1) < 0.5:
                    bonus += 10

                # Pump magnitude similarity
                if abs(price_change - pattern_pump) / max(pattern_pump, 1) < 0.3:
                    bonus += 15

            except:
                continue

        # Pattern 2: Explosive combination
        if price_change > 200 and volume > 2000000 and market_cap < 500000:
            bonus += 20  # Classic moonshot setup

        return bonus

    async def analyze_and_signal(self, token: Dict) -> bool:
        """Analyze token and send signal if criteria met"""
        symbol = token.get('symbol', 'Unknown')
        address = token.get('address', '')

        # NUCLEAR PRECISION: 6-hour duplicate protection for surgical accuracy
        recent_cutoff = datetime.now() - timedelta(hours=6)
        if any(s['symbol'] == symbol and s['time'] > recent_cutoff for s in self.last_signals):
            return False

        # Calculate intelligence score (optimized for speed)
        analysis = self.calculate_intelligence_score(token)
        score = analysis['score']

        # MONEY PRINTER PRECISION - Real profitable opportunities
        if score < 70:  # Balanced threshold - catches real opportunities
            return False

        # Confidence rating
        if score >= 80:
            confidence = "ULTRA HIGH"
            confidence_emoji = "🔥🔥🔥"
        elif score >= 65:
            confidence = "HIGH"
            confidence_emoji = "🔥🔥"
        elif score >= 50:
            confidence = "MEDIUM"
            confidence_emoji = "🔥"
        else:
            confidence = "LOW"
            confidence_emoji = "⚡"

        # Generate intelligent signal
        dexscreener_link = f'https://dexscreener.com/solana/{address}'
        birdeye_link = f'https://birdeye.so/token/{address}'

        factors_text = "\n".join([f"• {factor}" for factor in analysis['factors'][:5]])

        message = f"""🚀 <b>INTELLIGENT MOONSHOT SIGNAL</b> {confidence_emoji}

💎 <b>Token:</b> ${symbol}
📈 <b>24h Change:</b> +{analysis['price_change']:.1f}%
💰 <b>Volume:</b> ${analysis['volume']:,.0f}
📊 <b>Market Cap:</b> ${analysis['market_cap']:,.0f}

🧠 <b>INTELLIGENCE FACTORS:</b>
{factors_text}

⭐ <b>Confidence Score:</b> {score}/100 ({confidence})
⏰ <b>Signal Time:</b> {datetime.now().strftime('%H:%M:%S')}

🔗 <b>LIVE CHARTS:</b>
• <a href="{dexscreener_link}">DexScreener</a>
• <a href="{birdeye_link}">Birdeye</a>

🎯 <b>Intelligence-backed opportunity detected</b>"""

        # Send signal
        success = await self.send_telegram(message)
        if success:
            # Track sent signal
            self.last_signals.append({
                'symbol': symbol,
                'score': score,
                'time': datetime.now()
            })

            # Keep only recent signals (6-hour window)
            cutoff_6h = datetime.now() - timedelta(hours=6)
            self.last_signals = [s for s in self.last_signals if s['time'] > cutoff_6h]

            print(f"📱 INTELLIGENT SIGNAL: ${symbol} (Score: {score}) - {confidence}")
            return True

        return False

    async def intelligent_scan_cycle(self, cycle_count: int):
        """Enhanced scanning with intelligence integration using shared data"""
        print(f"🧠 Intelligent scan cycle - {datetime.now().strftime('%H:%M:%S')}")

        # Refresh intelligence database every 30 cycles (5 minutes)
        if cycle_count % 30 == 0:
            self.refresh_intelligence_periodically()
            print("🔄 Intelligence database refreshed")

        # Get fresh token data from DATA_COLLECTOR (no API calls)
        tokens = self.get_fresh_tokens_from_collector()
        signals_sent = 0

        if not tokens:
            print("⚠️ Waiting for fresh token data from DATA_COLLECTOR...")
            return 0

        # Analyze tokens with NUCLEAR intelligence scoring
        high_confidence_tokens = []

        for token in tokens:
            try:
                # NUCLEAR intelligence scoring - only the absolute best (fast scoring)
                analysis = self.calculate_intelligence_score(token)
                if analysis['score'] >= 70:  # MONEY PRINTER threshold - real profit opportunities
                    high_confidence_tokens.append((token, analysis))
            except Exception as e:
                continue

        print(f"📊 Found {len(high_confidence_tokens)} high-confidence opportunities")

        # Send signals for top opportunities
        for token, analysis in high_confidence_tokens[:10]:  # Top 10 per cycle
            if await self.analyze_and_signal(token):
                signals_sent += 1
                await asyncio.sleep(1)  # Reduced rate limit for speed

        print(f"✅ Analyzed {len(tokens)} tokens - Sent {signals_sent} intelligent signals")
        return signals_sent

    async def start_intelligent_trading(self):
        """Start intelligent trading system"""
        startup_msg = f"""🧠 <b>INTELLIGENT HELIX TRADER STARTED</b>

🚀 Whale-intelligence backed signals active
📊 Moonshot pattern recognition enabled
🔥 Real-time confidence scoring
⚡ Enhanced 10-second scanning

💡 Intelligence Database: {len(self.intelligence_db)} tokens
📈 Moonshot Patterns: {len(self.moonshot_patterns)} historical
⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

<i>Rapid-fire intelligent signals incoming...</i>"""

        await self.send_telegram(startup_msg)
        print("📱 Intelligent startup notification sent")

        print("""
╔══════════════════════════════════════════════════════════════╗
║              INTELLIGENT HELIX TRADER ACTIVE                ║
║                WHALE-BACKED MOONSHOT SIGNALS                ║
╚══════════════════════════════════════════════════════════════╝

🧠 INTELLIGENCE-ENHANCED SCANNING
🔥 CONFIDENCE-SCORED SIGNALS
⚡ RAPID 10-SECOND CYCLES
📱 WHALE-BACKED TELEGRAM ALERTS
        """)

        cycle_count = 0
        total_signals = 0

        while True:
            try:
                cycle_count += 1
                signals_sent = await self.intelligent_scan_cycle(cycle_count)
                total_signals += signals_sent

                # Statistics every 10 cycles
                if cycle_count % 10 == 0:
                    print(f"""
📊 INTELLIGENT TRADER STATS
════════════════════════════
🔄 Cycles: {cycle_count}
📡 Total Signals: {total_signals}
🧠 Intelligence DB: {len(self.intelligence_db)} tokens
🎯 Recent Signals: {len(self.last_signals)}
                    """)

                # Faster cycles when finding signals, slower when quiet
                wait_time = 5 if signals_sent > 0 else 10
                print(f"💤 Next scan in {wait_time} seconds...")
                await asyncio.sleep(wait_time)

            except KeyboardInterrupt:
                print("\n🛑 Intelligent trading stopped")
                break
            except Exception as e:
                print(f"⚠️ Cycle error: {e}")
                await asyncio.sleep(30)

async def main():
    """Main entry point"""
    try:
        trader = IntelligentTrader()
        await trader.start_intelligent_trading()
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("Check your .env file has all required API keys")
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
    except Exception as e:
        print(f"❌ System Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())