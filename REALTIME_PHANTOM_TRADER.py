#!/usr/bin/env python3
"""
REAL-TIME PHANTOM WALLET TRADER
===============================
Integrates screenshot monitoring with trading signals based on
Phantom wallet activity and new 2025 features.
"""

import asyncio
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
from PHANTOM_MONITOR import PhantomMonitor
from PHANTOM_OCR_ANALYZER import PhantomOCRAnalyzer
import aiohttp
import os

# Load environment
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

class RealtimePhantomTrader:
    """Real-time trader that monitors Phantom wallet and generates signals"""

    def __init__(self):
        self.monitor = PhantomMonitor()
        self.ocr_analyzer = PhantomOCRAnalyzer()

        # Trading configuration
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat = os.getenv('TELEGRAM_CHAT_ID')
        self.birdeye_key = os.getenv('BIRDEYE_API_KEY')

        # Trading state
        self.phantom_signals = []
        self.last_signal_time = {}
        self.trading_active = True

        # Signal thresholds
        self.SIGNAL_THRESHOLDS = {
            'min_confidence_score': 70,
            'psol_staking_bonus': 25,
            'token_pages_trending_bonus': 20,
            'swap_activity_bonus': 15,
            'new_feature_bonus': 30
        }

        print("""
╔══════════════════════════════════════════════════════════════╗
║              REAL-TIME PHANTOM WALLET TRADER                 ║
║          Screenshot + OCR + Signal Generation                ║
╚══════════════════════════════════════════════════════════════╝

🎯 Monitoring Phantom 2025 Features:
• PSOL Liquid Staking Activity
• Token Pages Trending Analysis
• Cross-Chain Swap Monitoring
• Multi-Chain Portfolio Tracking
• Enhanced Security Detection
        """)

    async def send_telegram_signal(self, message: str) -> bool:
        """Send trading signal to Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat,
                'text': message,
                'parse_mode': 'HTML'
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data, timeout=10) as response:
                    return response.status == 200

        except Exception as e:
            print(f"⚠️ Telegram error: {e}")
            return False

    def calculate_phantom_signal_score(self, phantom_data: dict) -> dict:
        """Calculate trading signal score based on Phantom activity"""
        try:
            score = 0
            factors = []

            features = phantom_data.get('phantom_features', {})
            market_data = phantom_data.get('market_data', {})
            new_features = phantom_data.get('new_features_detected', [])
            base_confidence = phantom_data.get('confidence_score', 0)

            # Base confidence from OCR quality
            score += min(base_confidence, 30)
            factors.append(f"OCR Confidence: {base_confidence}/100")

            # PSOL Staking Activity Signal
            if features.get('psol_staking_visible', False):
                score += self.SIGNAL_THRESHOLDS['psol_staking_bonus']
                factors.append("🔥 PSOL Liquid Staking Active")

            # Token Pages Trending Signal
            if features.get('token_pages_active', False):
                trending_tokens = market_data.get('trending_tokens', [])
                if len(trending_tokens) > 0:
                    score += self.SIGNAL_THRESHOLDS['token_pages_trending_bonus']
                    factors.append(f"📈 Token Pages: {len(trending_tokens)} trending")

                    # Extra bonus for multiple trending tokens
                    if len(trending_tokens) >= 3:
                        score += 10
                        factors.append("🚀 Multiple trending tokens")

            # Swap Activity Signal
            if features.get('swap_interface_open', False):
                score += self.SIGNAL_THRESHOLDS['swap_activity_bonus']
                factors.append("🔄 Active Swap Interface")

            # Portfolio Activity Signal
            balance = features.get('portfolio_balance')
            if balance and balance > 1000:  # Significant portfolio
                score += 15
                factors.append(f"💰 Active Portfolio: ${balance:,.0f}")

            # New Features Detection Bonus
            if new_features:
                bonus = min(len(new_features) * 10, self.SIGNAL_THRESHOLDS['new_feature_bonus'])
                score += bonus
                factors.append(f"✨ New Features: {', '.join(new_features)}")

            # Transaction Activity Bonus
            if features.get('transaction_pending', False):
                score += 20
                factors.append("⚡ Active Transaction Detected")

            # Market Momentum Analysis
            price_changes = market_data.get('price_changes', {})
            positive_changes = [token for token, change in price_changes.items()
                              if '+' in change and float(change.replace('%', '').replace('+', '')) > 5]

            if len(positive_changes) >= 2:
                score += 25
                factors.append(f"📊 Multiple Pumps: {len(positive_changes)} tokens")

            return {
                'score': min(score, 100),
                'factors': factors,
                'trending_tokens': market_data.get('trending_tokens', []),
                'active_features': [f for f in new_features],
                'portfolio_value': balance
            }

        except Exception as e:
            print(f"⚠️ Signal scoring error: {e}")
            return {'score': 0, 'factors': ['Scoring error']}

    async def generate_phantom_trading_signal(self, phantom_analysis: dict, signal_score: dict):
        """Generate and send trading signal based on Phantom activity"""
        try:
            score = signal_score['score']
            factors = signal_score['factors']
            trending_tokens = signal_score.get('trending_tokens', [])

            # Check if signal meets threshold
            if score < self.SIGNAL_THRESHOLDS['min_confidence_score']:
                return False

            # Anti-spam protection
            current_time = datetime.now()
            signal_key = f"phantom_{current_time.hour}"

            if signal_key in self.last_signal_time:
                time_diff = current_time - self.last_signal_time[signal_key]
                if time_diff < timedelta(minutes=15):  # 15-minute cooldown
                    return False

            # Confidence tier
            if score >= 90:
                confidence_tier = "NUCLEAR 🔥🔥🔥"
            elif score >= 80:
                confidence_tier = "ULTRA HIGH 🔥🔥"
            elif score >= 70:
                confidence_tier = "HIGH 🔥"
            else:
                confidence_tier = "MEDIUM ⚡"

            # Generate signal message
            factors_text = "\n".join([f"• {factor}" for factor in factors[:6]])
            trending_text = ", ".join(trending_tokens[:3]) if trending_tokens else "None detected"

            message = f"""🎯 <b>PHANTOM WALLET ACTIVITY SIGNAL</b> {confidence_tier.split()[1]}

📱 <b>Phantom Analysis Score:</b> {score}/100
🎪 <b>Confidence Level:</b> {confidence_tier}

🔍 <b>DETECTED PHANTOM ACTIVITY:</b>
{factors_text}

📈 <b>Trending Tokens:</b> {trending_text}
⏰ <b>Signal Time:</b> {current_time.strftime('%H:%M:%S')}

🚀 <b>PHANTOM-POWERED TRADING OPPORTUNITY</b>
💡 Based on real-time wallet activity monitoring

<i>Signal generated from live Phantom wallet screenshots</i>"""

            # Send signal
            success = await self.send_telegram_signal(message)
            if success:
                self.last_signal_time[signal_key] = current_time
                self.phantom_signals.append({
                    'timestamp': current_time.isoformat(),
                    'score': score,
                    'trending_tokens': trending_tokens,
                    'phantom_features': signal_score.get('active_features', [])
                })
                print(f"📱 PHANTOM SIGNAL SENT: Score {score} - {confidence_tier}")
                return True

            return False

        except Exception as e:
            print(f"⚠️ Signal generation error: {e}")
            return False

    async def run_realtime_phantom_trading(self, capture_interval=2):
        """Main real-time trading loop with Phantom monitoring"""
        print(f"""
🚀 REAL-TIME PHANTOM TRADING ACTIVE
═══════════════════════════════════
• Screenshot Capture: Every {capture_interval}s
• OCR Analysis: Real-time
• Signal Generation: Automatic
• Phantom Features: 2025 Updates
        """)

        cycle_count = 0

        try:
            while self.trading_active:
                cycle_start = time.time()
                cycle_count += 1

                print(f"\n🔄 Phantom Cycle #{cycle_count} - {datetime.now().strftime('%H:%M:%S')}")

                # Capture screenshot
                screenshot_path = self.monitor.capture_screenshot()

                if screenshot_path:
                    # Analyze screenshot with OCR
                    phantom_analysis = self.ocr_analyzer.process_screenshot(screenshot_path)

                    if phantom_analysis:
                        # Calculate signal score
                        signal_score = self.calculate_phantom_signal_score(phantom_analysis)

                        print(f"📊 Phantom Analysis: {signal_score['score']}/100")

                        # Generate trading signal if criteria met
                        if signal_score['score'] >= self.SIGNAL_THRESHOLDS['min_confidence_score']:
                            await self.generate_phantom_trading_signal(phantom_analysis, signal_score)

                        # Save analysis data
                        self.monitor.save_extracted_data(phantom_analysis)

                # Performance stats every 30 cycles
                if cycle_count % 30 == 0:
                    print(f"\n📊 SESSION STATS:")
                    print(f"• Screenshots: {self.monitor.screenshot_count}")
                    print(f"• Signals Sent: {len(self.phantom_signals)}")
                    print(f"• Cycles Completed: {cycle_count}")

                # Maintain timing
                elapsed = time.time() - cycle_start
                sleep_time = max(0, capture_interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)

        except KeyboardInterrupt:
            print(f"\n🛑 Phantom Trading Stopped")
            print(f"📊 Final Stats: {len(self.phantom_signals)} signals generated")
        except Exception as e:
            print(f"❌ Phantom trading error: {e}")

async def main():
    """Main entry point"""
    try:
        trader = RealtimePhantomTrader()

        print("🎮 PHANTOM TRADING OPTIONS:")
        print("1. Start real-time monitoring (2-second intervals)")
        print("2. Test single screenshot analysis")
        print("3. Analyze existing screenshots")

        choice = input("\nSelect option (1-3): ").strip()

        if choice == '1':
            await trader.run_realtime_phantom_trading(2)
        elif choice == '2':
            screenshot_path = trader.monitor.capture_screenshot()
            if screenshot_path:
                analysis = trader.ocr_analyzer.process_screenshot(screenshot_path)
                score = trader.calculate_phantom_signal_score(analysis)
                print(f"✅ Analysis complete: {score}")
        elif choice == '3':
            screenshots_dir = trader.monitor.screenshots_dir
            results = trader.ocr_analyzer.batch_analyze_screenshots(str(screenshots_dir))
            print(f"✅ Analyzed {len(results)} screenshots")
        else:
            print("Invalid option")

    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
    except Exception as e:
        print(f"❌ System Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())