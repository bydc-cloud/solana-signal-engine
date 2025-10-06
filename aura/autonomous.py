"""
AURA Autonomous Action Engine
Monitors signals and takes intelligent actions based on rules and memory
"""
import logging
from typing import Dict, List
from datetime import datetime

from .database import db
from .memory import memory
from .mcps.crypto_mcp import crypto_mcp

# Import MCP Toolkit for autonomous tool use
try:
    from .mcp_toolkit import mcp_toolkit
    MCP_TOOLKIT_AVAILABLE = True
except ImportError:
    mcp_toolkit = None
    MCP_TOOLKIT_AVAILABLE = False

logger = logging.getLogger(__name__)


class AutonomousEngine:
    """
    Monitors Helix signals and takes autonomous actions:
    - Auto-add to watchlist
    - Execute strategy trades
    - Trigger alerts
    - Enrich token knowledge
    """

    def __init__(self):
        self.db = db
        self.memory = memory
        self.crypto_mcp = crypto_mcp
        self.last_processed_signal_id = 0

        # Import Telegram bot
        try:
            from .telegram_bot import telegram_bot
            self.telegram = telegram_bot
            logger.info("Telegram bot integrated with autonomous engine")
        except Exception as e:
            self.telegram = None
            logger.warning(f"Telegram bot not available: {e}")

    # ═══════════════════════════════════════════════════════════
    # AUTONOMOUS DISCOVERY (MCP TOOLS)
    # ═══════════════════════════════════════════════════════════

    def discover_trending_tokens(self) -> int:
        """
        🔧 MCP TOOL: Autonomously discover trending tokens using CoinGecko
        Called periodically by worker to find hot tokens
        Returns number of trending tokens added to watchlist
        """
        try:
            if not MCP_TOOLKIT_AVAILABLE:
                return 0

            import asyncio

            # Get trending tokens from CoinGecko MCP
            trending = asyncio.run(mcp_toolkit.get_trending_tokens())

            if not trending:
                logger.debug("No trending tokens from CoinGecko MCP")
                return 0

            added_count = 0
            for token_data in trending[:5]:  # Top 5 trending
                try:
                    symbol = token_data.get('symbol', '').upper()
                    coin_id = token_data.get('id', '')
                    market_cap_rank = token_data.get('market_cap_rank', 0)

                    logger.info(f"🔧 MCP: Discovered trending token {symbol} (rank #{market_cap_rank})")

                    # Check if already in watchlist
                    watchlist = self.db.get_watchlist()
                    if any(w.get("symbol") == symbol for w in watchlist):
                        continue

                    # Add to watchlist if not already there
                    reason = f"Trending on CoinGecko (rank #{market_cap_rank})"
                    alert_rules = {
                        "price_change_percent": 15,
                        "volume_spike_ratio": 3.0,
                    }

                    # Use coin_id as address (will be resolved later)
                    self.db.add_to_watchlist(coin_id, reason, alert_rules)

                    # Create alert
                    self.db.create_alert(
                        coin_id,
                        f"🔥 {symbol} is trending on CoinGecko (rank #{market_cap_rank})",
                        "medium",
                        metadata=token_data
                    )

                    added_count += 1

                except Exception as e:
                    logger.error(f"Process trending token error: {e}")
                    continue

            if added_count > 0:
                logger.info(f"🔧 MCP: Added {added_count} trending tokens to watchlist")

            return added_count

        except Exception as e:
            logger.error(f"Discover trending tokens error: {e}")
            return 0

    # ═══════════════════════════════════════════════════════════
    # SIGNAL MONITORING
    # ═══════════════════════════════════════════════════════════

    def process_new_signals(self) -> int:
        """
        Check for new Helix signals and process them
        Returns number of signals processed
        """
        try:
            # Get recent signals
            signals = self.db.get_recent_helix_signals(hours=1, limit=100)

            processed_count = 0
            for signal in signals:
                signal_id = signal["id"]

                # Skip if already processed
                if signal_id <= self.last_processed_signal_id:
                    continue

                # Process signal
                self._process_signal(signal)
                processed_count += 1
                self.last_processed_signal_id = signal_id

            if processed_count > 0:
                logger.info(f"Autonomous: Processed {processed_count} new signals")

            return processed_count

        except Exception as e:
            logger.error(f"Autonomous process signals error: {e}")
            return 0

    def _process_signal(self, signal: Dict) -> None:
        """Process a single signal"""
        try:
            address = signal["token_address"]
            symbol = signal["symbol"]
            momentum = signal["momentum_score"]
            payload = signal.get("payload", {})

            logger.info(f"Autonomous: Processing signal for {symbol} (momentum: {momentum})")

            # 1. Enrich token knowledge
            self._enrich_token(address, symbol, payload)

            # 2. Check if should auto-add to watchlist
            if self.db.get_config("auto_watchlist_enabled"):
                self._maybe_add_to_watchlist(address, symbol, momentum, payload)

            # 3. Evaluate strategy rules
            self._evaluate_strategies(address, symbol, momentum, payload)

            # 4. Check alert conditions
            self._check_alert_conditions(address, symbol, momentum, payload)

        except Exception as e:
            logger.error(f"Autonomous process signal error: {e}")

    # ═══════════════════════════════════════════════════════════
    # TOKEN ENRICHMENT
    # ═══════════════════════════════════════════════════════════

    def _enrich_token(self, address: str, symbol: str, payload: Dict) -> None:
        """Enrich token with additional data sources - USES MCP TOOLS"""
        try:
            # Store basic token info
            metadata = {
                "mc": payload.get("mc", 0),
                "liquidity": payload.get("liquidity", 0),
                "holders": payload.get("holders", 0),
                "price": payload.get("price", 0),
            }

            # 🔧 MCP TOOL: Get additional market data from CoinGecko
            if MCP_TOOLKIT_AVAILABLE:
                try:
                    import asyncio
                    # Try to get CoinGecko data
                    coingecko_data = asyncio.run(mcp_toolkit.get_token_market_data(symbol))
                    if coingecko_data:
                        metadata["coingecko_rank"] = coingecko_data.get("market_cap_rank", 0)
                        metadata["ath"] = coingecko_data.get("ath", 0)
                        metadata["ath_change_percent"] = coingecko_data.get("ath_change_percentage", 0)
                        metadata["price_change_24h"] = coingecko_data.get("price_change_percentage_24h", 0)

                        logger.info(f"🔧 MCP: Enriched {symbol} with CoinGecko data")

                        # Add fact from CoinGecko
                        self.db.add_token_fact(
                            address,
                            "market",
                            f"CoinGecko rank: #{coingecko_data.get('market_cap_rank', 'N/A')}, ATH: ${coingecko_data.get('ath', 0):.6f}",
                            "coingecko_mcp",
                            0.95
                        )
                except Exception as e:
                    logger.debug(f"CoinGecko MCP enrichment skipped: {e}")

            self.db.upsert_token(address, symbol, symbol, metadata)

            # Add fact from scanner
            self.db.add_token_fact(
                address,
                "technical",
                f"Scanner signal: momentum {payload.get('momentum_score', 0)}, volume ratio {payload.get('volume_ratio', 0)}",
                "helix_scanner",
                0.9
            )

            # 🔧 MCP TOOL: Scrape token page with Firecrawl
            if MCP_TOOLKIT_AVAILABLE:
                try:
                    import asyncio
                    # Scrape Birdeye page for additional context
                    birdeye_url = f"https://birdeye.so/token/{address}"
                    page_data = asyncio.run(mcp_toolkit.scrape_webpage(birdeye_url))

                    if page_data and len(page_data) > 100:
                        # Extract key info from scraped content
                        self.db.add_token_fact(
                            address,
                            "social",
                            f"Birdeye page data: {page_data[:200]}...",
                            "firecrawl_mcp",
                            0.8
                        )
                        logger.info(f"🔧 MCP: Scraped {symbol} Birdeye page")
                except Exception as e:
                    logger.debug(f"Firecrawl MCP scraping skipped: {e}")

            # Store in memory using MCP
            observations = [
                f"Detected by scanner at {datetime.now().isoformat()}",
                f"Momentum score: {payload.get('momentum_score', 0)}",
                f"Market cap: ${metadata['mc']:,.0f}",
                f"Liquidity: ${metadata['liquidity']:,.0f}",
            ]

            # Add CoinGecko observations if available
            if "coingecko_rank" in metadata:
                observations.append(f"CoinGecko rank: #{metadata['coingecko_rank']}")
                observations.append(f"24h price change: {metadata['price_change_24h']:.2f}%")

            # 🔧 MCP TOOL: Store in memory MCP
            if MCP_TOOLKIT_AVAILABLE:
                try:
                    import asyncio
                    asyncio.run(mcp_toolkit.remember_token(address, observations))
                    logger.info(f"🔧 MCP: Stored {symbol} in memory graph")
                except Exception as e:
                    logger.debug(f"Memory MCP storage skipped: {e}")

            # Fallback to local memory
            self.memory.remember_token(address, observations)

            logger.info(f"Autonomous: Enriched {symbol} with MCP tools")

        except Exception as e:
            logger.error(f"Autonomous enrich token error: {e}")

    # ═══════════════════════════════════════════════════════════
    # WATCHLIST MANAGEMENT
    # ═══════════════════════════════════════════════════════════

    def _maybe_add_to_watchlist(self, address: str, symbol: str, momentum: float, payload: Dict) -> None:
        """Maybe add token to watchlist based on criteria"""
        try:
            threshold = self.db.get_config("scanner_signal_threshold", 65)

            if momentum >= threshold:
                # Check if already in watchlist
                watchlist = self.db.get_watchlist()
                if any(w["token_address"] == address for w in watchlist):
                    logger.debug(f"Autonomous: {symbol} already in watchlist")
                    return

                # Add to watchlist
                reason = f"Auto-added by scanner (momentum: {momentum:.1f})"
                alert_rules = {
                    "price_change_percent": 10,
                    "volume_spike_ratio": 2.0,
                    "momentum_threshold": threshold - 5,
                }

                self.db.add_to_watchlist(address, reason, alert_rules)

                # Create alert
                self.db.create_alert(
                    address,
                    f"🔍 {symbol} auto-added to watchlist (momentum: {momentum:.1f})",
                    "medium",
                    metadata=payload
                )

                logger.info(f"Autonomous: Added {symbol} to watchlist")

        except Exception as e:
            logger.error(f"Autonomous watchlist error: {e}")

    # ═══════════════════════════════════════════════════════════
    # STRATEGY EXECUTION
    # ═══════════════════════════════════════════════════════════

    def _evaluate_strategies(self, address: str, symbol: str, momentum: float, payload: Dict) -> None:
        """Evaluate if signal matches any active strategy rules"""
        try:
            if not self.db.get_config("paper_trading_enabled"):
                return

            strategies = self.db.get_active_strategies()

            for strategy in strategies:
                rules = strategy["rules"]
                entry_rules = rules.get("entry", {})

                # Check if signal matches entry conditions
                if self._check_entry_rules(entry_rules, momentum, payload):
                    self._execute_strategy_entry(strategy, address, symbol, payload)

        except Exception as e:
            logger.error(f"Autonomous evaluate strategies error: {e}")

    def _check_entry_rules(self, rules: Dict, momentum: float, payload: Dict) -> bool:
        """Check if signal meets strategy entry rules"""
        try:
            # Check momentum
            momentum_rule = rules.get("momentum", {})
            if "gte" in momentum_rule:
                if momentum < momentum_rule["gte"]:
                    return False

            # Check volume ratio
            volume_ratio = payload.get("volume_ratio", 0)
            volume_rule = rules.get("volume_ratio", {})
            if "gte" in volume_rule:
                if volume_ratio < volume_rule["gte"]:
                    return False

            # Check buy volume
            buy_volume = payload.get("helius_buy_volume_1h_usd", 0)
            buy_volume_rule = rules.get("buy_volume_1h_usd", {})
            if "gte" in buy_volume_rule:
                if buy_volume < buy_volume_rule["gte"]:
                    return False

            return True

        except Exception as e:
            logger.error(f"Check entry rules error: {e}")
            return False

    def _execute_strategy_entry(self, strategy: Dict, address: str, symbol: str, payload: Dict) -> None:
        """Execute strategy entry (paper trading)"""
        try:
            # Check max concurrent positions
            open_positions = self.db.get_open_positions()
            max_positions = self.db.get_config("max_concurrent_positions", 5)

            if len(open_positions) >= max_positions:
                logger.info(f"Autonomous: Max positions reached ({max_positions}), skipping {symbol}")
                return

            # Calculate position size
            price = payload.get("price", 0)
            if price == 0:
                logger.warning(f"Autonomous: No price for {symbol}, skipping")
                return

            position_size_usd = self.db.get_config("default_position_size_usd", 1000)
            amount = position_size_usd / price

            # Record trade
            self.db.add_strategy_trade(
                strategy["id"],
                address,
                "buy",
                price,
                amount,
                f"Auto-entry by {strategy['name']}"
            )

            # Add to portfolio
            notes = f"Strategy: {strategy['name']}, Entry reason: Momentum {payload.get('momentum_score', 0)}"
            self.db.add_position(address, price, amount, notes)

            # Create alert
            self.db.create_alert(
                address,
                f"🤖 Strategy '{strategy['name']}' opened position in {symbol} at ${price:.6f}",
                "high",
                metadata=payload
            )

            # Remember in memory
            self.memory.remember_strategy_result(
                strategy["name"],
                [f"Entered {symbol} at ${price:.6f} with momentum {payload.get('momentum_score', 0)}"]
            )

            logger.info(f"Autonomous: Executed strategy entry {symbol} @ ${price:.6f}")

        except Exception as e:
            logger.error(f"Autonomous execute strategy error: {e}")

    # ═══════════════════════════════════════════════════════════
    # ALERT CONDITIONS
    # ═══════════════════════════════════════════════════════════

    def _check_alert_conditions(self, address: str, symbol: str, momentum: float, payload: Dict) -> None:
        """Check if signal triggers any alert configs"""
        try:
            with self.db._get_conn() as conn:
                cur = conn.cursor()
                import json

                cur.execute("""
                    SELECT id, name, conditions, actions, priority
                    FROM alert_configs
                    WHERE enabled = 1
                """)

                for row in cur.fetchall():
                    config_id, name, conditions_json, actions_json, priority = row

                    try:
                        conditions = json.loads(conditions_json)
                        actions = json.loads(actions_json)

                        # Check conditions
                        if self._check_conditions(conditions, momentum, payload):
                            # Trigger actions
                            self._execute_alert_actions(config_id, actions, address, symbol, payload, priority)

                    except Exception as e:
                        logger.error(f"Check alert config {config_id} error: {e}")

        except Exception as e:
            logger.error(f"Check alert conditions error: {e}")

    def _check_conditions(self, conditions: Dict, momentum: float, payload: Dict) -> bool:
        """Check if conditions are met"""
        try:
            # Check momentum
            momentum_cond = conditions.get("momentum", {})
            if "gte" in momentum_cond and momentum < momentum_cond["gte"]:
                return False

            # Check volume ratio
            volume_ratio = payload.get("volume_ratio", 0)
            volume_cond = conditions.get("volume_ratio", {})
            if "gte" in volume_cond and volume_ratio < volume_cond["gte"]:
                return False

            return True

        except Exception as e:
            logger.error(f"Check conditions error: {e}")
            return False

    def _execute_alert_actions(self, config_id: int, actions: Dict, address: str, symbol: str, payload: Dict, priority: str) -> None:
        """Execute alert actions"""
        try:
            # Notify
            if actions.get("notify"):
                message = f"⚠️ Alert triggered for {symbol}: {payload.get('momentum_score', 0)} momentum"
                self.db.create_alert(address, message, priority, config_id, payload)

            # Auto-add to watchlist
            if actions.get("auto_add_watchlist"):
                watchlist = self.db.get_watchlist()
                if not any(w["token_address"] == address for w in watchlist):
                    self.db.add_to_watchlist(
                        address,
                        "Auto-added by alert trigger",
                        {"price_change_percent": 10}
                    )

            logger.info(f"Autonomous: Executed alert actions for {symbol}")

        except Exception as e:
            logger.error(f"Execute alert actions error: {e}")


# Singleton instance
autonomous_engine = AutonomousEngine()
