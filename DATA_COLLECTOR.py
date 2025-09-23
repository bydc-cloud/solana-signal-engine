#!/usr/bin/env python3
"""
HELIX DATA COLLECTOR - MOONSHOT INTELLIGENCE BUILDER
===================================================
Massive data ingestion system that builds intelligence database
for moonshot prediction. Runs parallel to WORKING_TRADER.py.

DOES NOT INTERFERE WITH CURRENT SYSTEM.
"""

import asyncio
import aiohttp
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional, Any

# Load environment (same as WORKING_TRADER.py)
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

class MoonshotDataCollector:
    """Massive scale data collector for moonshot intelligence"""

    def __init__(self):
        self.birdeye_key = os.getenv('BIRDEYE_API_KEY')
        self.helius_key = os.getenv('HELIUS_API_KEY')

        if not self.birdeye_key:
            raise ValueError("BIRDEYE_API_KEY required")

        # Create data directory
        self.data_dir = Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)

        # Database files
        self.all_tokens_file = self.data_dir / "all_tokens.json"
        self.whale_wallets_file = self.data_dir / "whale_wallets.json"
        self.transaction_patterns_file = self.data_dir / "transaction_patterns.json"
        self.moonshot_history_file = self.data_dir / "moonshot_history.json"
        self.fresh_tokens_file = self.data_dir / "fresh_tokens.json"  # For INTELLIGENT_TRADER

        # Initialize databases
        self.all_tokens = self.load_json(self.all_tokens_file, {})
        self.whale_wallets = self.load_json(self.whale_wallets_file, {})
        self.transaction_patterns = self.load_json(self.transaction_patterns_file, [])
        self.moonshot_history = self.load_json(self.moonshot_history_file, [])

        # Performance tracking
        self.tokens_processed = 0
        self.whales_identified = 0
        self.patterns_found = 0
        self.start_time = datetime.now()

    def load_json(self, file_path: Path, default: Any) -> Any:
        """Load JSON file or return default"""
        try:
            if file_path.exists():
                with open(file_path, 'r') as f:
                    return json.load(f)
        except:
            pass
        return default

    def save_json(self, data: Any, file_path: Path):
        """Save data to JSON file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save {file_path}: {e}")

    async def get_all_tokens_batch(self, offset: int = 0, limit: int = 50) -> List[Dict]:
        """Get batch of all tokens from Birdeye"""
        try:
            url = "https://public-api.birdeye.so/defi/tokenlist"
            headers = {'X-API-KEY': self.birdeye_key}
            params = {
                'sort_by': 'v24hUSD',
                'sort_type': 'desc',
                'offset': offset,
                'limit': limit
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params, timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('data', {}).get('tokens', [])
            return []
        except Exception as e:
            print(f"⚠️ Batch fetch error (offset {offset}): {e}")
            return []

    async def analyze_token_for_whale_activity(self, token: Dict) -> Optional[Dict]:
        """Analyze token for whale activity patterns"""
        try:
            symbol = token.get('symbol', 'Unknown')
            address = token.get('address', '')

            # Safe float conversion with None handling
            price_change_24h = float(token.get('priceChange24hPercent') or 0)
            volume_24h = float(token.get('v24hUSD') or 0)
            market_cap = float(token.get('mc') or 0)

            # Skip tokens with no meaningful data
            if volume_24h == 0 and market_cap == 0:
                return None

            # Whale activity indicators
            whale_indicators = {
                'high_volume_low_mcap': volume_24h > 100000 and market_cap < 1000000,
                'sudden_volume_spike': volume_24h > market_cap * 0.5,
                'price_volume_divergence': price_change_24h > 50 and volume_24h > 500000,
                'small_cap_moonshot': market_cap < 100000 and price_change_24h > 100
            }

            whale_score = sum(whale_indicators.values())

            if whale_score >= 2:  # Significant whale activity
                return {
                    'symbol': symbol,
                    'address': address,
                    'timestamp': datetime.now().isoformat(),
                    'price_change_24h': price_change_24h,
                    'volume_24h': volume_24h,
                    'market_cap': market_cap,
                    'whale_score': whale_score,
                    'indicators': whale_indicators
                }

        except Exception as e:
            print(f"⚠️ Token analysis error: {e}")

        return None

    async def identify_moonshot_patterns(self, token_data: Dict):
        """Identify potential moonshot patterns"""
        try:
            # Moonshot pattern detection
            price_change = token_data.get('price_change_24h', 0)
            volume = token_data.get('volume_24h', 0)
            market_cap = token_data.get('market_cap', 0)

            # Historical moonshot signatures
            if price_change > 200 and volume > 1000000:  # 200%+ pump with high volume
                moonshot_pattern = {
                    'token': token_data['symbol'],
                    'address': token_data['address'],
                    'timestamp': datetime.now().isoformat(),
                    'pump_magnitude': price_change,
                    'volume_signature': volume,
                    'market_cap_at_pump': market_cap,
                    'pattern_type': 'historical_moonshot'
                }

                self.moonshot_history.append(moonshot_pattern)
                self.patterns_found += 1

                print(f"🚀 MOONSHOT PATTERN: ${token_data['symbol']} (+{price_change:.1f}%) - Volume: ${volume:,.0f}")

        except Exception as e:
            print(f"⚠️ Pattern analysis error: {e}")

    async def massive_token_scan(self):
        """Scan all tokens in parallel batches"""
        print(f"🔍 Starting massive token scan - {datetime.now().strftime('%H:%M:%S')}")

        # Parallel batch processing
        batch_size = 50
        max_tokens = 2000  # Start with 2000, will increase as system proves stable

        tasks = []
        for offset in range(0, max_tokens, batch_size):
            task = asyncio.create_task(self.get_all_tokens_batch(offset, batch_size))
            tasks.append(task)

        # Execute all batches in parallel
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        all_new_tokens = []
        successful_batches = 0

        for batch_result in batch_results:
            if isinstance(batch_result, list):
                all_new_tokens.extend(batch_result)
                successful_batches += 1
            elif isinstance(batch_result, Exception):
                print(f"⚠️ Batch failed: {batch_result}")

        print(f"✅ Processed {len(all_new_tokens)} tokens from {successful_batches} batches")

        # Analyze each token for whale activity
        whale_activities = []

        for token in all_new_tokens:
            whale_activity = await self.analyze_token_for_whale_activity(token)
            if whale_activity:
                whale_activities.append(whale_activity)
                await self.identify_moonshot_patterns(whale_activity)

            self.tokens_processed += 1

            # Store token data with safe float conversion
            address = token.get('address', '')
            if address:
                try:
                    self.all_tokens[address] = {
                        'symbol': token.get('symbol', 'Unknown'),
                        'last_scan': datetime.now().isoformat(),
                        'volume_24h': float(token.get('v24hUSD') or 0),
                        'market_cap': float(token.get('mc') or 0),
                        'price_change_24h': float(token.get('priceChange24hPercent') or 0)
                    }
                except (ValueError, TypeError):
                    # Skip tokens with invalid data
                    continue

        if whale_activities:
            print(f"🐋 Found {len(whale_activities)} whale activities")

        # Save fresh tokens for INTELLIGENT_TRADER
        fresh_data = {
            'timestamp': datetime.now().isoformat(),
            'tokens': all_new_tokens,
            'total_count': len(all_new_tokens)
        }
        self.save_json(fresh_data, self.fresh_tokens_file)
        print(f"📊 Fresh tokens saved for intelligent trader: {len(all_new_tokens)}")

        return len(all_new_tokens), len(whale_activities)

    async def save_intelligence_database(self):
        """Save all collected intelligence to files"""
        try:
            self.save_json(self.all_tokens, self.all_tokens_file)
            self.save_json(self.whale_wallets, self.whale_wallets_file)
            self.save_json(self.transaction_patterns, self.transaction_patterns_file)
            self.save_json(self.moonshot_history, self.moonshot_history_file)

            print(f"💾 Intelligence database saved - {len(self.all_tokens)} tokens tracked")
        except Exception as e:
            print(f"❌ Database save error: {e}")

    def print_intelligence_stats(self):
        """Print current intelligence statistics"""
        runtime = datetime.now() - self.start_time

        print(f"""
📊 MOONSHOT INTELLIGENCE STATS
════════════════════════════════════
⏱️  Runtime: {runtime}
🔍 Tokens Processed: {self.tokens_processed:,}
📈 Moonshot Patterns: {len(self.moonshot_history)}
🐋 Whale Activities: {len(self.transaction_patterns)}
💾 Database Size: {len(self.all_tokens):,} tokens
        """)

    async def continuous_intelligence_gathering(self):
        """Main intelligence gathering loop"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║                HELIX MOONSHOT DATA COLLECTOR                 ║
║               BUILDING INTELLIGENCE DATABASE                 ║
╚══════════════════════════════════════════════════════════════╝

🧠 MASSIVE SCALE DATA COLLECTION ACTIVE
📊 Building moonshot prediction database
🔍 Scanning thousands of tokens every cycle
⚡ Parallel processing for maximum speed

🔗 This runs alongside your WORKING_TRADER.py
📱 No interference with your current signals
🚀 Building intelligence for future moonshot predictions
        """)

        cycle_count = 0

        while True:
            try:
                cycle_start = time.time()
                cycle_count += 1

                print(f"\n🔄 Intelligence Cycle #{cycle_count} - {datetime.now().strftime('%H:%M:%S')}")

                # Massive token scan
                tokens_scanned, whale_activities = await self.massive_token_scan()

                # Save intelligence database
                await self.save_intelligence_database()

                # Print statistics
                if cycle_count % 5 == 0:  # Every 5 cycles
                    self.print_intelligence_stats()

                cycle_time = time.time() - cycle_start
                print(f"⚡ Cycle completed in {cycle_time:.1f}s - Next in 60s")

                # Wait before next cycle
                await asyncio.sleep(60)  # 60 second cycles

            except KeyboardInterrupt:
                print("\n🛑 Intelligence gathering stopped by user")
                break
            except Exception as e:
                print(f"❌ Intelligence cycle error: {e}")
                await asyncio.sleep(30)  # Wait and continue

async def main():
    """Main entry point"""
    try:
        collector = MoonshotDataCollector()
        await collector.continuous_intelligence_gathering()
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("Check your .env file has BIRDEYE_API_KEY")
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
    except Exception as e:
        print(f"❌ System Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())