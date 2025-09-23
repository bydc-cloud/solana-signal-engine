#!/usr/bin/env python3
"""
REALITY MOMENTUM SCANNER
=======================
Production-ready momentum scanner with advanced volume validation and risk filtering.
Deploys the working signal generation system for continuous operation.
"""

import asyncio
import requests
import time
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import aiohttp
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('momentum_scanner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

class RealityMomentumScanner:
    """Production momentum scanner with enhanced risk filtering"""

    def __init__(self):
        self.birdeye_key = os.getenv('BIRDEYE_API_KEY')
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat = os.getenv('TELEGRAM_CHAT_ID')

        # Risk management
        self.sent_signals = set()  # Track sent signals to avoid spam
        self.signal_history = []   # Track signal performance
        self.last_scan_time = 0
        self.min_scan_interval = 300  # 5 minutes between scans

        print("""
╔══════════════════════════════════════════════════════════════╗
║              REALITY MOMENTUM SCANNER v1.0                  ║
║            Production-Ready Signal Generation                ║
╚══════════════════════════════════════════════════════════════╝

✅ Enhanced volume validation
✅ Advanced risk filtering
✅ Anti-spam protection
✅ Performance tracking
✅ Production logging
        """)

    def get_market_data(self) -> list:
        """Get market data with proven working API calls"""
        all_tokens = []

        if not self.birdeye_key:
            logger.error("No Birdeye API key available")
            return []

        # Multi-strategy approach for comprehensive coverage
        strategies = [
            ('Volume Leaders', {'sort_by': 'v24hUSD', 'sort_type': 'desc', 'limit': 50}),
            ('Price Gainers', {'sort_by': 'v24hChangePercent', 'sort_type': 'desc', 'limit': 50}),
        ]

        for strategy_name, params in strategies:
            try:
                logger.info(f"Scanning {strategy_name}...")

                url = "https://public-api.birdeye.so/defi/tokenlist"
                headers = {'X-API-KEY': self.birdeye_key}

                response = requests.get(url, headers=headers, params=params, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    tokens = data.get('data', {}).get('tokens', [])

                    # Add strategy info to each token
                    for token in tokens:
                        token['discovery_strategy'] = strategy_name
                        token['scan_time'] = datetime.now().isoformat()

                    all_tokens.extend(tokens)
                    logger.info(f"Retrieved {len(tokens)} tokens from {strategy_name}")

                else:
                    logger.warning(f"{strategy_name} API error: {response.status_code}")

                time.sleep(1)  # Rate limiting

            except Exception as e:
                logger.error(f"Strategy {strategy_name} error: {e}")
                continue

        # Remove duplicates by address
        unique_tokens = {}
        for token in all_tokens:
            address = token.get('address', '')
            if address and address not in unique_tokens:
                unique_tokens[address] = token

        final_tokens = list(unique_tokens.values())
        logger.info(f"Total unique tokens: {len(final_tokens)}")

        return final_tokens

    def advanced_volume_validation(self, token: dict) -> dict:
        """Enhanced volume validation with detailed risk assessment"""
        validation_result = {
            'is_valid': False,
            'risk_score': 100,  # 0-100, lower is better
            'risk_factors': [],
            'volume_quality': 0  # 0-100, higher is better
        }

        try:
            volume_24h = token.get('v24hUSD', 0) or 0
            market_cap = token.get('mc', 0) or 0
            price_change = token.get('v24hChangePercent', 0) or 0
            liquidity = token.get('liquidity', 0) or 0
            price = token.get('price', 0) or 0

            risk_score = 0
            quality_score = 0

            # Volume analysis
            if volume_24h < 50000:  # Less than $50k volume
                validation_result['risk_factors'].append('Low volume')
                risk_score += 30
            elif volume_24h >= 100000:  # Over $100k volume
                quality_score += 20

            # Market cap validation
            if market_cap <= 0:
                validation_result['risk_factors'].append('Invalid market cap')
                risk_score += 50
                return validation_result
            elif market_cap < 20000:  # Under $20k mcap
                validation_result['risk_factors'].append('Very low market cap')
                risk_score += 25
            elif 50000 <= market_cap <= 10000000:  # Sweet spot
                quality_score += 15

            # Volume to market cap ratio
            volume_ratio = volume_24h / market_cap if market_cap > 0 else 0
            if volume_ratio < 0.1:  # Less than 10% daily turnover
                validation_result['risk_factors'].append('Low turnover')
                risk_score += 20
            elif volume_ratio >= 0.5:  # 50%+ daily turnover
                quality_score += 20
            elif volume_ratio > 5.0:  # Over 500% turnover (suspicious)
                validation_result['risk_factors'].append('Excessive turnover')
                risk_score += 15

            # Liquidity validation
            if liquidity <= 0:
                validation_result['risk_factors'].append('No liquidity data')
                risk_score += 10
            elif liquidity < 25000:  # Less than $25k liquidity
                validation_result['risk_factors'].append('Low liquidity')
                risk_score += 20
            elif liquidity >= 100000:  # Over $100k liquidity
                quality_score += 15

            # Price movement validation
            abs_change = abs(price_change) if price_change is not None else 0
            if abs_change > 1000000:  # Extreme price change (likely error)
                validation_result['risk_factors'].append('Extreme price movement')
                risk_score += 40
            elif abs_change >= 50:  # Significant movement
                quality_score += 10
            elif abs_change < 5:  # Minimal movement
                validation_result['risk_factors'].append('Low price momentum')
                risk_score += 15

            # Price validation
            if price <= 0:
                validation_result['risk_factors'].append('Invalid price')
                risk_score += 30

            validation_result['risk_score'] = min(risk_score, 100)
            validation_result['volume_quality'] = min(quality_score, 100)
            validation_result['is_valid'] = risk_score < 50 and quality_score >= 30

            return validation_result

        except Exception as e:
            logger.error(f"Volume validation error: {e}")
            validation_result['risk_factors'].append('Validation error')
            return validation_result

    def calculate_signal_strength(self, token: dict, validation: dict) -> float:
        """Calculate final signal strength with risk adjustment"""
        try:
            base_score = 0

            volume_24h = token.get('v24hUSD', 0) or 0
            market_cap = token.get('mc', 0) or 0
            price_change_raw = token.get('v24hChangePercent', 0)
            price_change = abs(price_change_raw) if price_change_raw is not None else 0
            liquidity = token.get('liquidity', 0) or 0

            # Volume momentum (35%)
            if market_cap > 0:
                volume_ratio = volume_24h / market_cap
                if volume_ratio >= 2.0:
                    base_score += 35
                elif volume_ratio >= 1.0:
                    base_score += 30
                elif volume_ratio >= 0.5:
                    base_score += 25
                elif volume_ratio >= 0.2:
                    base_score += 15

            # Price momentum (30%)
            if price_change >= 100:
                base_score += 30
            elif price_change >= 50:
                base_score += 25
            elif price_change >= 25:
                base_score += 20
            elif price_change >= 15:
                base_score += 15

            # Liquidity factor (20%)
            if liquidity > 0 and market_cap > 0:
                liq_ratio = liquidity / market_cap
                if liq_ratio >= 0.3:
                    base_score += 20
                elif liq_ratio >= 0.1:
                    base_score += 15
                elif liq_ratio >= 0.05:
                    base_score += 10

            # Volume quality bonus (10%)
            quality_bonus = validation['volume_quality'] * 0.1
            base_score += quality_bonus

            # Risk adjustment
            risk_penalty = validation['risk_score'] * 0.3  # Up to 30 point penalty
            final_score = max(base_score - risk_penalty, 0)

            # Market cap preference (5%)
            if 100000 <= market_cap <= 5000000:  # 100k-5M sweet spot
                final_score += 5

            return min(final_score, 100)

        except Exception as e:
            logger.error(f"Signal strength calculation error: {e}")
            return 0

    def should_send_signal(self, token: dict, signal_strength: float) -> bool:
        """Determine if signal should be sent based on advanced criteria"""
        try:
            address = token.get('address', '')
            symbol = token.get('symbol', '')

            # Minimum signal strength
            if signal_strength < 75:  # Raised threshold for quality
                return False

            # Check if already sent recently
            if address in self.sent_signals:
                logger.info(f"Signal already sent for {symbol}")
                return False

            # Check for obvious scam tokens
            scam_keywords = ['SCAM', 'RUG', 'FAKE', 'TEST', 'DEAD']
            if any(keyword in symbol.upper() for keyword in scam_keywords):
                logger.warning(f"Potential scam token detected: {symbol}")
                return False

            # Skip major tokens
            major_tokens = ['SOL', 'USDC', 'USDT', 'BTC', 'ETH', 'WBTC', 'WETH']
            if symbol.upper() in major_tokens:
                return False

            return True

        except Exception as e:
            logger.error(f"Signal decision error: {e}")
            return False

    async def send_enhanced_signal(self, token: dict, signal_strength: float, validation: dict):
        """Send enhanced signal with risk information"""
        try:
            symbol = token.get('symbol', '')
            address = token.get('address', '')
            price = token.get('price', 0)
            volume = token.get('v24hUSD', 0)
            mcap = token.get('mc', 0)
            change = token.get('v24hChangePercent', 0)
            strategy = token.get('discovery_strategy', 'Unknown')

            # Risk level determination
            risk_score = validation['risk_score']
            if risk_score <= 20:
                risk_level = "🟢 LOW"
            elif risk_score <= 40:
                risk_level = "🟡 MEDIUM"
            else:
                risk_level = "🔴 HIGH"

            # Signal strength emoji
            if signal_strength >= 90:
                strength_emoji = "🚀"
            elif signal_strength >= 80:
                strength_emoji = "⚡"
            else:
                strength_emoji = "📈"

            jupiter_link = f"https://jup.ag/swap/SOL-{address}"

            message = f"""{strength_emoji} <b>MOMENTUM SIGNAL</b> {strength_emoji}

💎 <b>Token:</b> ${symbol}
🎯 <b>Signal Strength:</b> {signal_strength:.1f}/100
⚠️ <b>Risk Level:</b> {risk_level}

💰 <b>Price:</b> ${price:.8f}
📊 <b>24h Change:</b> {change:+.1f}%
💸 <b>Volume:</b> ${volume:,.0f}
🎯 <b>Market Cap:</b> ${mcap:,.0f}

📈 <b>Volume Quality:</b> {validation['volume_quality']}/100
🔍 <b>Discovery:</b> {strategy}

🔗 <b>Trade:</b> <a href="{jupiter_link}">Jupiter Swap</a>

⏰ {datetime.now().strftime('%H:%M:%S')}

<b>🎯 REALITY MOMENTUM SCANNER</b>
<i>Advanced risk-filtered signals</i>"""

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
                        logger.info(f"Signal sent: ${symbol} (Strength: {signal_strength:.1f})")

                        # Track sent signal
                        self.sent_signals.add(address)
                        self.signal_history.append({
                            'symbol': symbol,
                            'address': address,
                            'signal_strength': signal_strength,
                            'risk_score': risk_score,
                            'sent_time': datetime.now().isoformat()
                        })

                        return True
                    else:
                        logger.error(f"Telegram error: HTTP {response.status}")

        except Exception as e:
            logger.error(f"Enhanced signal send error: {e}")

        return False

    async def run_scan_cycle(self):
        """Run a complete scan cycle"""
        try:
            logger.info("Starting scan cycle...")

            # Get market data
            tokens = self.get_market_data()
            if not tokens:
                logger.warning("No market data retrieved")
                return 0

            signals_sent = 0
            processed_tokens = 0

            for token in tokens:
                try:
                    symbol = token.get('symbol', 'UNKNOWN')

                    # Skip obvious non-tokens
                    if not symbol or len(symbol) > 20:
                        continue

                    # Advanced volume validation
                    validation = self.advanced_volume_validation(token)
                    if not validation['is_valid']:
                        continue

                    # Calculate signal strength
                    signal_strength = self.calculate_signal_strength(token, validation)

                    # Check if should send signal
                    if self.should_send_signal(token, signal_strength):
                        success = await self.send_enhanced_signal(token, signal_strength, validation)
                        if success:
                            signals_sent += 1
                            await asyncio.sleep(3)  # Rate limiting between signals

                    processed_tokens += 1

                except Exception as e:
                    logger.error(f"Token processing error: {e}")
                    continue

            logger.info(f"Scan complete: {processed_tokens} processed, {signals_sent} signals sent")
            return signals_sent

        except Exception as e:
            logger.error(f"Scan cycle error: {e}")
            return 0

    async def run_continuous_scanner(self):
        """Run continuous momentum scanning"""
        logger.info("Starting continuous momentum scanner...")

        try:
            while True:
                current_time = time.time()

                # Check scan interval
                if current_time - self.last_scan_time >= self.min_scan_interval:
                    signals_sent = await self.run_scan_cycle()
                    self.last_scan_time = current_time

                    # Clear old sent signals (reset every hour)
                    if len(self.sent_signals) > 50:
                        self.sent_signals.clear()
                        logger.info("Cleared sent signals cache")

                    # Status update
                    if signals_sent > 0:
                        logger.info(f"✅ Sent {signals_sent} signals this cycle")
                    else:
                        logger.info("⏳ No qualifying signals found - continuing monitoring")

                await asyncio.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            logger.info("Scanner stopped by user")
        except Exception as e:
            logger.error(f"Scanner error: {e}")

async def main():
    """Deploy the reality momentum scanner"""
    try:
        scanner = RealityMomentumScanner()

        print("\n🚀 DEPLOYING REALITY MOMENTUM SCANNER...")
        print("📊 Advanced volume validation active")
        print("🛡️ Enhanced risk filtering enabled")
        print("⚡ Continuous signal generation starting...")
        print("\nPress Ctrl+C to stop\n")

        await scanner.run_continuous_scanner()

    except KeyboardInterrupt:
        print("\n🛑 Reality Momentum Scanner stopped")
    except Exception as e:
        logger.error(f"Deployment error: {e}")

if __name__ == "__main__":
    asyncio.run(main())