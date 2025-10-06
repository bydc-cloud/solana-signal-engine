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
        """Enrich token with additional data sources"""
        try:
            # Store basic token info
            metadata = {
                "mc": payload.get("mc", 0),
                "liquidity": payload.get("liquidity", 0),
                "holders": payload.get("holders", 0),
                "price": payload.get("price", 0),
            }

            self.db.upsert_token(address, symbol, symbol, metadata)

            # Add fact from scanner
            self.db.add_token_fact(
                address,
                "technical",
                f"Scanner signal: momentum {payload.get('momentum_score', 0)}, volume ratio {payload.get('volume_ratio', 0)}",
                "helix_scanner",
                0.9
            )

            # Store in memory
            observations = [
                f"Detected by scanner at {datetime.now().isoformat()}",
                f"Momentum score: {payload.get('momentum_score', 0)}",
                f"Market cap: ${metadata['mc']:,.0f}",
                f"Liquidity: ${metadata['liquidity']:,.0f}",
            ]
            self.memory.remember_token(address, observations)

            logger.info(f"Autonomous: Enriched {symbol}")

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
