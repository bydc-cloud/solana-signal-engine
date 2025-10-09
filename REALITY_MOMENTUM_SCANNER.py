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
from zoneinfo import ZoneInfo
import aiohttp
import logging

# Graduation system - uses Helius/Birdeye/Nansen instead of Pump.fun
try:
    from graduation.config import grad_cfg
    from graduation.detectors import bootstrap_detectors
except Exception:  # Graduation package optional
    grad_cfg = None
    bootstrap_detectors = None


# Birdeye discovery strategies are tuned to cover different market segments
SCAN_STRATEGIES = [
    ("High Volume", {'sort_by': 'v24hUSD', 'sort_type': 'desc', 'limit': 50}),
    ("Top Gainers", {'sort_by': 'v24hChangePercent', 'sort_type': 'desc', 'limit': 50}),
    ("Deep Liquidity", {'sort_by': 'liquidity', 'sort_type': 'desc', 'limit': 50}),
    ("Micro Caps", {'sort_by': 'mc', 'sort_type': 'asc', 'limit': 50}),
    ("Recent Listings", {'sort_by': 'createdTime', 'sort_type': 'desc', 'limit': 50}),
    ("Price Momentum", {'sort_by': 'v1hChangePercent', 'sort_type': 'desc', 'limit': 50}),
]

# Scanner tuning - AGGRESSIVE SIGNAL MODE - maximize signal generation
DEFAULT_SIGNAL_THRESHOLD = 20  # Lower threshold for more signals
DEFAULT_DUPLICATE_COOLDOWN_MINUTES = 30  # Shorter cooldown for faster re-evaluation
MAX_TOKENS_PER_SCAN = 300  # Process more tokens per scan

# Target band for current request
TARGET_MARKET_CAP_MIN = 10_000
TARGET_MARKET_CAP_MAX = 50_000  # Increased max cap
MAX_MICROCAP_FETCH_PAGES = 4  # More pages for comprehensive discovery
MAX_V24H_USD = 10_000_000  # Higher volume ceiling
HELIUS_ACTIVITY_CHUNK = 100  # More data per request
HELIUS_CONCURRENCY = 12  # Higher concurrency
HELIUS_REQUEST_LIMIT = 100  # More transactions per request
HELIUS_CACHE_TTL_SECONDS = 300  # Shorter cache for fresher data

# Buyer momentum heuristics - RELAXED FOR LEARNING
MIN_HOLDER_COUNT = 5  # Lower minimum for more opportunities
MAX_HOLDER_COUNT = 300  # Higher maximum to include more tokens
MIN_BUYER_DOMINANCE = 0.45  # Lower threshold
MIN_BUY_VOLUME_1H_USD = 300  # Lower volume requirement
MIN_BUYERS_1H = 2  # Lower buyer count
MAX_DETAIL_CONCURRENCY = 8  # Higher concurrency for faster enrichment
DETAIL_TIMEOUT_SECONDS = 8  # Longer timeout to avoid failures
WATCHLIST_COOLDOWN_MINUTES = 15  # Shorter watchlist cooldown

# Setup logging with rotation to prevent filling Railway volume
from logging.handlers import RotatingFileHandler

log_handler = RotatingFileHandler(
    'momentum_scanner.log',
    maxBytes=50_000_000,  # 50 MB max per file
    backupCount=2,  # Keep 2 old files (150 MB total max)
)
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        log_handler,
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
        self.helius_key = os.getenv('HELIUS_API_KEY')
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat = os.getenv('TELEGRAM_CHAT_ID')
        self.watchlist_chat = os.getenv('TELEGRAM_WATCHLIST_CHAT_ID') or self.telegram_chat

        # Risk management / adaptive tuning
        self.sent_signals = {}  # address -> datetime of last alert
        self.watchlist_sent = {}
        self.watchlist_cooldown = timedelta(minutes=WATCHLIST_COOLDOWN_MINUTES)
        self.helius_cache = {}
        self.helius_cache_ttl = timedelta(seconds=HELIUS_CACHE_TTL_SECONDS)
        self.signal_history = []
        self.last_scan_time = 0
        self.min_scan_interval = 120  # 2 minutes between scans for more frequent opportunities
        self.signal_threshold = DEFAULT_SIGNAL_THRESHOLD
        self.duplicate_cooldown = timedelta(minutes=DEFAULT_DUPLICATE_COOLDOWN_MINUTES)
        self.max_tokens = MAX_TOKENS_PER_SCAN
        self.signal_timezone = ZoneInfo("America/Los_Angeles")
        self.graduation_task = None

        self.base_min_buyers_1h = MIN_BUYERS_1H
        self.base_min_buyer_dominance = MIN_BUYER_DOMINANCE
        self.base_min_buy_volume_usd = MIN_BUY_VOLUME_1H_USD
        self.dynamic_min_buyers_1h = self.base_min_buyers_1h
        self.dynamic_min_buyer_dominance = self.base_min_buyer_dominance
        self.dynamic_min_buy_volume_usd = self.base_min_buy_volume_usd
        self.empty_cycles = 0

        metrics_dir = Path(__file__).parent / "data"
        metrics_dir.mkdir(exist_ok=True)
        self.metrics_path = metrics_dir / "scanner_metrics.json"
        self.metrics = {
            'cycles': 0,
            'signals': 0,
            'watchlist_alerts': 0,
            'empty_cycles': 0,
            'avg_cycle_seconds': 0.0,
            'last_cycle_seconds': 0.0,
        }

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

    def fetch_tokens_from_birdeye(self, strategy_name: str, params: dict, retries: int = 2) -> list:
        """Query Birdeye with retries and verbose logging on failure"""
        if not self.birdeye_key:
            logger.error("No Birdeye API key available")
            return []

        url = "https://public-api.birdeye.so/defi/tokenlist"
        headers = {
            'X-API-KEY': self.birdeye_key,
            'x-chain': 'solana',
        }
        query = dict(params)
        query.setdefault('chain', 'solana')

        for attempt in range(retries + 1):
            try:
                logger.info(f"Scanning {strategy_name} (attempt {attempt + 1})...")
                response = requests.get(url, headers=headers, params=query, timeout=8)

                if response.status_code != 200:
                    body_preview = response.text[:200]
                    logger.warning(
                        "%s API error %s: %s",
                        strategy_name,
                        response.status_code,
                        body_preview,
                    )
                else:
                    try:
                        payload = response.json()
                    except ValueError as json_error:
                        logger.error(f"{strategy_name} JSON decode error: {json_error}")
                        payload = None

                    if payload and payload.get('success'):
                        tokens = payload.get('data', {}).get('tokens', [])
                        now_iso = datetime.now().isoformat()
                        for token in tokens:
                            token['discovery_strategy'] = strategy_name
                            token['scan_time'] = now_iso
                        logger.info(f"Retrieved {len(tokens)} tokens from {strategy_name}")
                        return tokens

            except requests.RequestException as request_error:
                logger.error(f"{strategy_name} request error: {request_error}")

            sleep_time = 1.5 * (attempt + 1)
            logger.debug(f"Retrying {strategy_name} in {sleep_time:.1f}s")
            time.sleep(sleep_time)

        logger.error(f"{strategy_name} failed after {retries + 1} attempts")
        return []

    def fetch_additional_microcaps(self, target_count: int = 60) -> list:
        """Sweep low market cap pages to backfill the 10-30k band with per-page timeout"""
        collected = []
        sweep_stats = {'pages_fetched': 0, 'pages_failed': 0, 'tokens_added': 0}

        for page in range(MAX_MICROCAP_FETCH_PAGES):
            offset = page * 50
            params = {
                'sort_by': 'mc',
                'sort_type': 'asc',
                'limit': 50,
                'offset': offset,
            }

            page_start = time.time()
            try:
                # Per-page timeout of 6s, single retry
                tokens = self.fetch_tokens_from_birdeye(f"Micro Cap Sweep p{page + 1}", params, retries=1)
                page_duration = time.time() - page_start

                if page_duration > 6.0:
                    logger.warning(f"Micro cap page {page+1} took {page_duration:.1f}s (>6s threshold)")

                if not tokens:
                    sweep_stats['pages_failed'] += 1
                    logger.debug(f"Micro cap page {page+1} returned no tokens")
                    continue

                sweep_stats['pages_fetched'] += 1
                added_this_page = 0
                for token in tokens:
                    market_cap = token.get('mc') or 0
                    if TARGET_MARKET_CAP_MIN <= market_cap <= TARGET_MARKET_CAP_MAX:
                        collected.append(token)
                        added_this_page += 1

                sweep_stats['tokens_added'] += added_this_page
                logger.debug(f"Micro cap page {page+1} added {added_this_page} tokens (total: {len(collected)})")

                if len(collected) >= target_count:
                    logger.info(f"Micro cap sweep reached target ({target_count}), stopping early")
                    break

                time.sleep(0.5)

            except requests.RequestException as e:
                sweep_stats['pages_failed'] += 1
                logger.warning(f"Micro cap page {page+1} request failed: {e}")
                continue
            except Exception as e:
                sweep_stats['pages_failed'] += 1
                logger.error(f"Micro cap page {page+1} unexpected error: {e}")
                continue

        logger.info(
            f"Micro cap sweep: {len(collected)} tokens collected "
            f"(pages: {sweep_stats['pages_fetched']} ok, {sweep_stats['pages_failed']} failed, "
            f"tokens added: {sweep_stats['tokens_added']})"
        )
        return collected

    def get_top_tokens(self) -> list:
        """Aggregate token lists across discovery strategies with deduping"""
        aggregated = []
        discovery_counts = {}

        for strategy_name, params in SCAN_STRATEGIES:
            tokens = self.fetch_tokens_from_birdeye(strategy_name, params)
            discovery_counts[strategy_name] = len(tokens)
            if tokens:
                aggregated.extend(tokens)
            time.sleep(0.75)

        if not aggregated:
            logger.error("Birdeye returned zero tokens across all strategies")
            return []

        unique_tokens = {}
        for token in aggregated:
            address = token.get('address')
            if not address:
                continue
            # Keep the highest volume snapshot when duplicates appear
            if address not in unique_tokens:
                unique_tokens[address] = token
            else:
                existing = unique_tokens[address]
                if (token.get('v24hUSD') or 0) > (existing.get('v24hUSD') or 0):
                    unique_tokens[address] = token

        final_tokens = list(unique_tokens.values())
        final_tokens.sort(key=lambda t: t.get('v24hUSD') or 0, reverse=True)
        if len(final_tokens) > self.max_tokens:
            final_tokens = final_tokens[:self.max_tokens]

        filtered_tokens = [
            token for token in final_tokens
            if TARGET_MARKET_CAP_MIN <= (token.get('mc') or 0) <= TARGET_MARKET_CAP_MAX
            and (token.get('v24hUSD') or 0) <= MAX_V24H_USD
        ]

        if len(filtered_tokens) < 25:
            # Re-enabled micro cap sweep with hardened error handling
            logger.info(f"Triggering micro cap sweep (current: {len(filtered_tokens)} tokens, target: ≥40)")
            sweep_tokens = self.fetch_additional_microcaps(target_count=60)
            if sweep_tokens:
                filtered_tokens.extend(sweep_tokens)
                logger.info(f"After sweep: {len(filtered_tokens)} tokens")

            # Dedup after merging sweep results
            dedup = {}
            for token in filtered_tokens:
                address = token.get('address')
                if not address:
                    continue
                if address not in dedup:
                    dedup[address] = token
            filtered_tokens = list(dedup.values())

        # Enforce MAX_TOKENS_PER_SCAN cap after sweep
        if len(filtered_tokens) > self.max_tokens:
            filtered_tokens = filtered_tokens[:self.max_tokens]
            logger.debug(f"Capped to MAX_TOKENS_PER_SCAN ({self.max_tokens})")

        if len(filtered_tokens) < 20:
            fallback_tokens = [
                token for token in final_tokens
                if 8_000 <= (token.get('mc') or 0) <= 40_000
                and (token.get('v24hUSD') or 0) <= MAX_V24H_USD
            ]
            for token in fallback_tokens:
                if token not in filtered_tokens:
                    filtered_tokens.append(token)

        dedup_final = {}
        for token in filtered_tokens:
            address = token.get('address')
            if not address:
                continue
            if address not in dedup_final:
                dedup_final[address] = token
        filtered_tokens = list(dedup_final.values())

        filtered_tokens.sort(key=lambda t: t.get('v24hUSD') or 0, reverse=True)

        summary = ", ".join(f"{name}:{count}" for name, count in discovery_counts.items())
        logger.info(
            "Token discovery summary -> unique:%d filtered:%d (%s)",
            len(final_tokens),
            len(filtered_tokens),
            summary,
        )

        return filtered_tokens

    def get_market_data(self) -> list:
        """Backward compatible wrapper used by the rest of the scanner"""
        return self.get_top_tokens()

    def prune_sent_signals(self):
        """Drop cached signals that are outside the cooldown window"""
        if not self.sent_signals:
            return

        cutoff = datetime.now() - self.duplicate_cooldown
        before = len(self.sent_signals)
        self.sent_signals = {
            addr: ts for addr, ts in self.sent_signals.items() if ts >= cutoff
        }

        if len(self.sent_signals) < before:
            logger.debug(
                "Pruned %d cached signals outside %d minute cooldown",
                before - len(self.sent_signals),
                self.duplicate_cooldown.total_seconds() / 60,
            )

    def prune_watchlist_sent(self):
        if not self.watchlist_sent:
            return

        cutoff = datetime.now() - self.watchlist_cooldown
        before = len(self.watchlist_sent)
        self.watchlist_sent = {
            addr: ts for addr, ts in self.watchlist_sent.items() if ts >= cutoff
        }

        if len(self.watchlist_sent) < before:
            logger.debug(
                "Pruned %d watchlist entries outside %d minute cooldown",
                before - len(self.watchlist_sent),
                self.watchlist_cooldown.total_seconds() / 60,
            )

    def prune_helius_cache(self):
        if not self.helius_cache:
            return

        cutoff = datetime.now() - self.helius_cache_ttl
        before = len(self.helius_cache)
        self.helius_cache = {
            mint: entry
            for mint, entry in self.helius_cache.items()
            if entry.get('fetched_at') and entry['fetched_at'] >= cutoff
        }

        if len(self.helius_cache) < before:
            logger.debug(
                "Pruned %d Helius cache entries", before - len(self.helius_cache)
            )

    def has_recent_signal(self, address: str) -> bool:
        """Check if we alerted on this address within the cooldown"""
        if not address:
            return False

        last_sent = self.sent_signals.get(address)
        if not last_sent:
            return False

        return datetime.now() - last_sent < self.duplicate_cooldown

    def has_recent_watchlist(self, address: str) -> bool:
        if not address:
            return False

        last_sent = self.watchlist_sent.get(address)
        if not last_sent:
            return False

        return datetime.now() - last_sent < self.watchlist_cooldown

    async def enrich_token_metrics(self, tokens: list) -> list:
        """Fetch Birdeye overview data to evaluate buyer momentum and holders"""
        if not tokens or not self.birdeye_key:
            return tokens

        url = "https://public-api.birdeye.so/defi/token_overview"
        headers = {
            'X-API-KEY': self.birdeye_key,
            'x-chain': 'solana',
        }

        semaphore = asyncio.Semaphore(MAX_DETAIL_CONCURRENCY)

        async def load_overview(session: aiohttp.ClientSession, token: dict):
            address = token.get('address')
            if not address:
                token['overview'] = {}
                return

            params = {'address': address}

            try:
                async with semaphore:
                    async with session.get(url, headers=headers, params=params, timeout=DETAIL_TIMEOUT_SECONDS) as resp:
                        if resp.status == 200:
                            payload = await resp.json()
                            overview = payload.get('data') or {}
                            token['overview'] = overview
                        else:
                            logger.warning(f"Overview HTTP {resp.status} for {address}")
                            token['overview'] = {}
            except Exception as exc:
                logger.error(f"Overview fetch error for {address}: {exc}")
                token['overview'] = {}

            overview = token.get('overview') or {}
            token['holders'] = overview.get('holder')
            token['buy5m'] = overview.get('buy5m') or 0
            token['trade5m'] = overview.get('trade5m') or 0
            token['buy1h'] = overview.get('buy1h') or 0
            token['trade1h'] = overview.get('trade1h') or 0
            token['unique_wallets_1h'] = overview.get('uniqueWallet1h') or 0
            token['unique_wallets_24h'] = overview.get('uniqueWallet24h') or 0
            token['price_change_1h'] = overview.get('priceChange1hPercent')
            token['price_change_5m'] = overview.get('priceChange5mPercent')
            token['vbuy1h_usd'] = overview.get('vBuy1hUSD') or 0
            token['v1h_usd'] = overview.get('v1hUSD') or 0
            token['buy24h'] = overview.get('buy24h') or 0

        async with aiohttp.ClientSession() as session:
            await asyncio.gather(*(load_overview(session, token) for token in tokens))

        return tokens

    async def fetch_helius_activity(self, tokens: list) -> list:
        """Use Helius transactions to augment recent wallet activity."""
        if not tokens or not self.helius_key:
            return tokens

        semaphore = asyncio.Semaphore(HELIUS_CONCURRENCY)
        base_url = "https://api.helius.xyz/v0/addresses"
        now_epoch = time.time()
        cache_cutoff = datetime.now() - self.helius_cache_ttl

        async def load_activity(session: aiohttp.ClientSession, token: dict):
            mint = token.get('address')
            if not mint:
                return

            cached = self.helius_cache.get(mint)
            if cached and cached.get('fetched_at') and cached['fetched_at'] >= cache_cutoff:
                self._apply_helius_stats(token, cached.get('stats') or {})
                return

            params = {
                'api-key': self.helius_key,
                'limit': HELIUS_REQUEST_LIMIT,
            }

            url = f"{base_url}/{mint}/transactions"

            try:
                async with semaphore:
                    async with session.get(url, params=params, timeout=12) as response:
                        if response.status != 200:
                            logger.debug("Helius activity fetch failed (%s) for %s: %s", response.status, mint, await response.text())
                            return

                        data = await response.json()

            except Exception as exc:
                logger.debug("Helius activity error for %s: %s", mint, exc)
                return

            unique_5m = set()
            unique_1h = set()
            unique_24h = set()
            buy_volume_tokens_1h = 0.0
            tx_count_1h = 0
            last_activity_minutes = None

            price = float(token.get('price') or 0)

            for tx in data:
                ts = tx.get('timestamp')
                if not ts:
                    continue

                age_minutes = (now_epoch - ts) / 60.0
                transfers = tx.get('tokenTransfers') or []
                relevant = False

                for transfer in transfers:
                    if transfer.get('mint') != mint:
                        continue

                    relevant = True
                    to_user = transfer.get('toUserAccount')
                    from_user = transfer.get('fromUserAccount')

                    amount_raw = transfer.get('tokenAmount') or 0
                    try:
                        amount_tokens = float(amount_raw)
                    except (TypeError, ValueError):
                        amount_tokens = 0.0

                    if age_minutes <= 5:
                        if to_user:
                            unique_5m.add(to_user)
                        if from_user:
                            unique_5m.add(from_user)

                    if age_minutes <= 60:
                        tx_count_1h += 1
                        if to_user:
                            unique_1h.add(to_user)
                            if amount_tokens > 0:
                                buy_volume_tokens_1h += amount_tokens
                        if from_user:
                            unique_1h.add(from_user)

                    if age_minutes <= 24 * 60:
                        if to_user:
                            unique_24h.add(to_user)
                        if from_user:
                            unique_24h.add(from_user)

                if relevant:
                    if last_activity_minutes is None or age_minutes < last_activity_minutes:
                        last_activity_minutes = age_minutes

            stats = {
                'unique_1h': len(unique_1h),
                'unique_5m': len(unique_5m),
                'unique_24h': len(unique_24h),
                'buy_volume_tokens_1h': buy_volume_tokens_1h,
                'buy_volume_usd_1h': buy_volume_tokens_1h * price if price > 0 else 0.0,
                'transactions_1h': tx_count_1h,
                'last_activity_minutes': last_activity_minutes,
            }

            self._apply_helius_stats(token, stats)
            self.helius_cache[mint] = {
                'fetched_at': datetime.now(),
                'stats': stats,
            }

        async with aiohttp.ClientSession() as session:
            await asyncio.gather(
                *(load_activity(session, token) for token in tokens[:HELIUS_ACTIVITY_CHUNK])
            )

        return tokens

    def _apply_helius_stats(self, token: dict, stats: dict):
        if not stats:
            return

        unique_1h = stats.get('unique_1h') or 0
        unique_5m = stats.get('unique_5m') or 0
        unique_24h = stats.get('unique_24h') or 0
        buy_volume_tokens = stats.get('buy_volume_tokens_1h') or 0.0
        buy_volume_usd = stats.get('buy_volume_usd_1h') or 0.0
        tx_count_1h = stats.get('transactions_1h') or 0
        last_activity = stats.get('last_activity_minutes')

        if unique_1h:
            token['helius_unique_wallets_1h'] = unique_1h
            token['unique_wallets_1h'] = token.get('unique_wallets_1h') or unique_1h
        if unique_5m:
            token['helius_unique_wallets_5m'] = unique_5m
            if not token.get('buy5m'):
                token['buy5m'] = unique_5m
        if unique_24h:
            token['helius_unique_wallets_24h'] = unique_24h
        if buy_volume_usd:
            token['helius_buy_volume_1h_usd'] = buy_volume_usd
            if buy_volume_usd > float(token.get('vbuy1h_usd') or 0):
                token['vbuy1h_usd'] = buy_volume_usd
        token['helius_buy_volume_1h'] = buy_volume_tokens
        if tx_count_1h:
            token['helius_transactions_1h'] = tx_count_1h
        if last_activity is not None:
            token['helius_last_activity_minutes'] = last_activity

    def should_watchlist(self, token: dict, validation: dict, signal_strength: float, reason: str) -> bool:
        address = token.get('address')
        if not address or not self.watchlist_chat:
            return False

        if self.has_recent_watchlist(address):
            return False

        risk_score = validation.get('risk_score', 100)
        momentum_score = validation.get('momentum_score', 0)
        helius_wallets = (
            token.get('helius_unique_wallets_1h')
            or token.get('unique_wallets_1h')
            or 0
        )
        helius_buy_usd = float(token.get('helius_buy_volume_1h_usd') or 0)
        last_trade = validation.get('last_trade_minutes') or token.get('helius_last_activity_minutes')

        if risk_score >= 85:
            return False
        if helius_wallets < max(2, self.dynamic_min_buyers_1h - 1):
            return False
        if helius_buy_usd < max(250, self.dynamic_min_buy_volume_usd * 0.4) and signal_strength < self.signal_threshold - 10:
            return False
        if momentum_score < 18:
            return False
        if last_trade is not None and last_trade > 90:
            return False

        return True

    async def send_watchlist_signal(self, token: dict, signal_strength: float, validation: dict, reason: str):
        try:
            symbol = token.get('symbol', '')
            address = token.get('address', '')
            if not address:
                return False

            holders = int(token.get('holders') or 0)
            buy1h = int(token.get('buy1h') or 0)
            buy5m = int(token.get('buy5m') or 0)
            helius_wallets_1h = int(token.get('helius_unique_wallets_1h') or token.get('unique_wallets_1h') or 0)
            helius_buy_usd = float(token.get('helius_buy_volume_1h_usd') or 0)
            helius_tx_1h = int(token.get('helius_transactions_1h') or 0)
            dominance = validation.get('buyer_dominance', 0)
            turnover = validation.get('volume_ratio', 0)
            momentum_score = validation.get('momentum_score', 0)
            risk_score = validation.get('risk_score', 0)
            last_trade = validation.get('last_trade_minutes') or token.get('helius_last_activity_minutes')

            if last_trade is not None:
                last_trade_label = f"{last_trade:.0f}m ago"
            else:
                last_trade_label = "unknown"

            jupiter_link = f"https://jup.ag/swap/SOL-{address}"
            dexscreener_link = f"https://dexscreener.com/solana/{address}"
            pst_time = datetime.now(self.signal_timezone).strftime('%Y-%m-%d %I:%M:%S %p %Z')

            message = f"""📝 <b>WATCHLIST SIGNAL</b> 📝

💎 <b>Token:</b> ${symbol}
🧾 <b>Address:</b> <code>{address}</code>
🎯 <b>Tentative Strength:</b> {signal_strength:.1f}/100
⚠️ <b>Risk Score:</b> {risk_score:.1f}
📋 <b>Reason:</b> {reason}

👥 <b>Holders:</b> {holders}
🛒 <b>Buys:</b> 1h {buy1h} | 5m {buy5m}
🤝 <b>Helius Wallets (1h):</b> {helius_wallets_1h}
💵 <b>Helius Buy Vol (1h):</b> ${helius_buy_usd:,.0f}
🔄 <b>Helius Tx (1h):</b> {helius_tx_1h}
🔥 <b>Buyer Dominance:</b> {dominance*100:.0f}%
📈 <b>Momentum Score:</b> {momentum_score:.1f}
🔁 <b>Turnover:</b> {turnover:.2f}x
⏱️ <b>Last Trade:</b> {last_trade_label}

🔗 <b>Jupiter:</b> <a href="{jupiter_link}">Swap</a>
📊 <b>DexScreener:</b> <a href="{dexscreener_link}">Live Chart</a>

⏰ {pst_time}

<b>👀 WATCHLIST ONLY</b>"""

            data = {
                'chat_id': self.watchlist_chat,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': False
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"https://api.telegram.org/bot{self.telegram_token}/sendMessage",
                    data=data,
                    timeout=15
                ) as response:
                    if response.status == 200:
                        self.watchlist_sent[address] = datetime.now()
                        return True
                    logger.error("Watchlist Telegram error: HTTP %s", response.status)
        except Exception as exc:
            logger.error("Watchlist send error: %s", exc)

        return False

    def prioritize_wallet_activity(self, tokens: list) -> list:
        """Sort tokens so high wallet/buyer activity is evaluated first"""
        def wallet_score(token: dict) -> tuple:
            unique_1h = (
                token.get('helius_unique_wallets_1h')
                or token.get('unique_wallets_1h')
                or 0
            )
            unique_5m = (
                token.get('helius_unique_wallets_5m')
                or token.get('buy5m')
                or 0
            )
            buy_volume_usd = (
                token.get('helius_buy_volume_1h_usd')
                or token.get('vBuy1hUSD')
                or 0
            )
            return (
                unique_1h,
                unique_5m,
                buy_volume_usd,
                token.get('helius_transactions_1h') or 0,
                token.get('v24hUSD') or 0,
            )

        tokens.sort(key=wallet_score, reverse=True)
        return tokens

    def adjust_adaptive_thresholds(self, signals_sent: int):
        previous = (
            self.dynamic_min_buyers_1h,
            self.dynamic_min_buyer_dominance,
            self.dynamic_min_buy_volume_usd,
        )

        if signals_sent > 0:
            self.empty_cycles = 0
            self.dynamic_min_buyers_1h = self.base_min_buyers_1h
            self.dynamic_min_buyer_dominance = self.base_min_buyer_dominance
            self.dynamic_min_buy_volume_usd = self.base_min_buy_volume_usd
        else:
            self.empty_cycles += 1
            step = min(self.empty_cycles // 3, 2)
            new_min_buyers = max(2, self.base_min_buyers_1h - step)
            new_min_dominance = max(0.45, round(self.base_min_buyer_dominance - 0.05 * step, 3))
            new_min_volume = max(300, round(self.base_min_buy_volume_usd * (0.8 ** step), 2))
            self.dynamic_min_buyers_1h = new_min_buyers
            self.dynamic_min_buyer_dominance = new_min_dominance
            self.dynamic_min_buy_volume_usd = new_min_volume

        if previous != (
            self.dynamic_min_buyers_1h,
            self.dynamic_min_buyer_dominance,
            self.dynamic_min_buy_volume_usd,
        ):
            logger.info(
                "Adaptive thresholds -> buyers:%s dominance:%.2f volume:$%s (empty cycles=%d)",
                self.dynamic_min_buyers_1h,
                self.dynamic_min_buyer_dominance,
                int(self.dynamic_min_buy_volume_usd),
                self.empty_cycles,
            )

    def record_cycle_metrics(self, signals_sent: int, filter_stats: dict, cycle_seconds: float):
        try:
            self.metrics['cycles'] += 1
            self.metrics['signals'] += signals_sent
            self.metrics['watchlist_alerts'] += filter_stats.get('watchlist', 0)
            self.metrics['empty_cycles'] = self.empty_cycles

            cycles = self.metrics['cycles']
            self.metrics['last_cycle_seconds'] = round(cycle_seconds, 3)
            avg_prev = self.metrics['avg_cycle_seconds']
            if cycles == 1:
                self.metrics['avg_cycle_seconds'] = round(cycle_seconds, 3)
            else:
                self.metrics['avg_cycle_seconds'] = round(((avg_prev * (cycles - 1)) + cycle_seconds) / cycles, 3)

            with self.metrics_path.open('w') as fp:
                json.dump(self.metrics, fp, indent=2)
        except Exception as exc:
            logger.debug("Metrics write error: %s", exc)

    def advanced_volume_validation(self, token: dict) -> dict:
        """Score fundamentals + live buyer momentum for the 10-30k band"""
        validation_result = {
            'is_valid': False,
            'risk_score': 100,
            'risk_factors': [],
            'volume_quality': 0,
            'volume_ratio': 0,
            'buyer_dominance': 0,
            'momentum_score': 0,
            'holders': token.get('holders'),
            'last_trade_minutes': None,
        }

        try:
            volume_24h = float(token.get('v24hUSD') or 0)
            market_cap = float(token.get('mc') or 0)
            price_change = token.get('v24hChangePercent')
            liquidity = float(token.get('liquidity') or 0)
            price = float(token.get('price') or 0)

            holders = token.get('holders')
            trades_1h = token.get('trade1h') or 0
            buys_1h = token.get('buy1h') or 0
            buy5m = token.get('buy5m') or 0
            trades_5m = token.get('trade5m') or 0
            unique_wallets_1h = (
                token.get('helius_unique_wallets_1h')
                or token.get('unique_wallets_1h')
                or 0
            )
            if not buy5m:
                buy5m = token.get('helius_unique_wallets_5m') or 0
            helius_tx_1h = token.get('helius_transactions_1h') or 0
            if helius_tx_1h and helius_tx_1h > trades_1h:
                trades_1h = helius_tx_1h
            vbuy1h_usd = float(token.get('vbuy1h_usd') or 0)
            helius_buy_usd = float(token.get('helius_buy_volume_1h_usd') or 0)
            if helius_buy_usd > vbuy1h_usd:
                vbuy1h_usd = helius_buy_usd
            price_change_1h = token.get('price_change_1h') or 0
            price_change_5m = token.get('price_change_5m') or 0
            buy24h = token.get('buy24h') or 0

            last_trade_unix = token.get('lastTradeUnixTime') or token.get('last_trade_unix_time')
            last_trade_minutes = token.get('helius_last_activity_minutes')
            if last_trade_minutes is None and last_trade_unix:
                from datetime import datetime
                last_trade_minutes = max((datetime.utcnow() - datetime.utcfromtimestamp(last_trade_unix)).total_seconds() / 60, 0)
            validation_result['last_trade_minutes'] = last_trade_minutes

            current_min_buyers = self.dynamic_min_buyers_1h
            current_min_dominance = self.dynamic_min_buyer_dominance
            current_min_buy_volume = self.dynamic_min_buy_volume_usd

            risk_score = 0
            quality_score = 0
            momentum_score = 0

            # 24h volume sanity for micro caps
            if volume_24h < 8000:
                validation_result['risk_factors'].append('Very low daily volume')
                risk_score += 30
            elif volume_24h < 20000:
                validation_result['risk_factors'].append('Light daily volume')
                risk_score += 10
                quality_score += 5
            else:
                quality_score += 20

            if market_cap <= 0:
                validation_result['risk_factors'].append('Invalid market cap')
                validation_result['risk_score'] = 100
                return validation_result

            if market_cap < TARGET_MARKET_CAP_MIN:
                validation_result['risk_factors'].append('Below target market cap')
                risk_score += 15
            elif market_cap > TARGET_MARKET_CAP_MAX:
                validation_result['risk_factors'].append('Above target market cap')
                risk_score += 25

            volume_ratio = volume_24h / market_cap if market_cap > 0 else 0
            validation_result['volume_ratio'] = volume_ratio

            if volume_ratio >= 200:
                validation_result['risk_factors'].append('Hyper turnover anomaly')
                risk_score += 45
            elif volume_ratio < 0.08:
                validation_result['risk_factors'].append('Thin turnover')
                risk_score += 15
            elif volume_ratio <= 2.5:
                quality_score += 15
            elif volume_ratio <= 5.0:
                quality_score += 10
            else:
                validation_result['risk_factors'].append('Suspicious turnover')
                risk_score += 10

            if liquidity < 2500:
                validation_result['risk_factors'].append('Low liquidity')
                risk_score += 18
            elif liquidity < 15000:
                risk_score += 5
                quality_score += 5
            else:
                quality_score += 15

            abs_change = abs(price_change) if price_change is not None else 0
            if abs_change > 600:
                validation_result['risk_factors'].append('Extreme 24h move')
                risk_score += 20
            elif abs_change >= 40:
                quality_score += 10

            if holders is None:
                validation_result['risk_factors'].append('Missing holder data')
                risk_score += 15
            else:
                if holders < MIN_HOLDER_COUNT:
                    validation_result['risk_factors'].append('Too few holders')
                    risk_score += 25
                elif holders > MAX_HOLDER_COUNT:
                    validation_result['risk_factors'].append('Crowded holder base')
                    risk_score += 30
                else:
                    quality_score += 18

            buyer_dominance = 0.0
            if trades_1h > 0:
                buyer_dominance = buys_1h / trades_1h
                validation_result['buyer_dominance'] = buyer_dominance
                if buyer_dominance >= current_min_dominance and buys_1h >= current_min_buyers:
                    quality_score += 25
                    momentum_score += 35
                elif buyer_dominance >= 0.5 and buys_1h >= max(3, current_min_buyers - 1):
                    quality_score += 12
                    momentum_score += 20
                else:
                    validation_result['risk_factors'].append('Weak buyer dominance')
                    risk_score += 12
            else:
                if buy24h >= max(current_min_buyers * 3, 20):
                    momentum_score += 18
                    quality_score += 8
                elif buy24h >= current_min_buyers * 2:
                    momentum_score += 10
                else:
                    validation_result['risk_factors'].append('No 1h trade data')
                    risk_score += 15

            if buy5m >= 2 and (trades_5m or 0) >= 2:
                momentum_score += 18
            elif buy5m == 0 and trades_5m == 0:
                momentum_score += 0
            elif buy5m == 0:
                validation_result['risk_factors'].append('No fresh buys (5m)')
                risk_score += 8

            if vbuy1h_usd >= current_min_buy_volume:
                momentum_score += 20
            elif vbuy1h_usd < max(250, current_min_buy_volume * 0.4):
                validation_result['risk_factors'].append('Minimal 1h buy volume')
                risk_score += 8

            if unique_wallets_1h >= current_min_buyers:
                quality_score += 10
            elif unique_wallets_1h <= 1:
                risk_score += 12

            if price_change_1h >= 20:
                momentum_score += 15
            elif price_change_1h < -5:
                validation_result['risk_factors'].append('1h price fading')
                risk_score += 8

            if price_change_5m >= 5:
                momentum_score += 8
            elif price_change_5m < -5:
                validation_result['risk_factors'].append('5m fade')
                risk_score += 5

            stale_spike_threshold = max(40, current_min_buyers * 10)
            if buys_1h < 2 and buy5m == 0 and buy24h and buy24h > stale_spike_threshold:
                validation_result['risk_factors'].append('Stale volume spike (24h only)')
                risk_score += 20

            if last_trade_minutes is not None:
                if last_trade_minutes <= 10:
                    momentum_score += 15
                elif last_trade_minutes <= 30:
                    momentum_score += 10
                elif last_trade_minutes <= 120:
                    quality_score += 5
                else:
                    validation_result['risk_factors'].append('Stale trading (>2h)')
                    risk_score += 20

            if price <= 0:
                validation_result['risk_factors'].append('Invalid price data')
                risk_score += 40

            validation_result['risk_score'] = min(risk_score, 100)
            validation_result['volume_quality'] = min(quality_score, 100)
            validation_result['momentum_score'] = min(momentum_score, 100)
            validation_result['buyer_dominance'] = buyer_dominance
            validation_result['is_valid'] = (
                validation_result['risk_score'] < 75
                and validation_result['volume_quality'] >= 12
                and validation_result['momentum_score'] >= 18
            )

            return validation_result

        except Exception as e:
            logger.error(f"Volume validation error: {e}")
            validation_result['risk_factors'].append('Validation error')
            return validation_result

    def calculate_signal_strength(self, token: dict, validation: dict) -> float:
        """Calculate final signal strength with buyer momentum emphasis"""
        try:
            base_score = 0.0

            volume_24h = float(token.get('v24hUSD') or 0)
            market_cap = float(token.get('mc') or 0)
            price_change_24h = token.get('v24hChangePercent') or 0
            price_change_1h = token.get('price_change_1h') or 0
            liquidity = float(token.get('liquidity') or 0)
            holders = token.get('holders') or 0

            if market_cap > 0:
                volume_ratio = volume_24h / market_cap
                if volume_ratio >= 1.2:
                    base_score += 24
                elif volume_ratio >= 0.7:
                    base_score += 20
                elif volume_ratio >= 0.3:
                    base_score += 15
                elif volume_ratio >= 0.15:
                    base_score += 10

            if market_cap > 0 and liquidity > 0:
                liq_ratio = liquidity / market_cap
                if liq_ratio >= 0.25:
                    base_score += 12
                elif liq_ratio >= 0.12:
                    base_score += 9
                elif liq_ratio >= 0.05:
                    base_score += 6

            if price_change_1h >= 25:
                base_score += 12
            elif price_change_1h >= 12:
                base_score += 8
            elif price_change_1h >= 5:
                base_score += 5

            if price_change_24h >= 60:
                base_score += 8
            elif price_change_24h >= 30:
                base_score += 6
            elif price_change_24h >= 15:
                base_score += 4

            helius_unique = token.get('helius_unique_wallets_1h') or 0
            if helius_unique >= 12:
                base_score += 10
            elif helius_unique >= 6:
                base_score += 7
            elif helius_unique >= 3:
                base_score += 4

            helius_buy_usd = token.get('helius_buy_volume_1h_usd') or 0
            if helius_buy_usd >= 3000:
                base_score += 8
            elif helius_buy_usd >= 1500:
                base_score += 6
            elif helius_buy_usd >= 500:
                base_score += 4

            momentum_score = validation.get('momentum_score', 0)
            base_score += momentum_score * 0.45

            volume_quality = validation.get('volume_quality', 0)
            base_score += volume_quality * 0.2

            buyer_dom = validation.get('buyer_dominance', 0)
            if buyer_dom > 0.5:
                base_score += (buyer_dom - 0.5) * 40

            if MIN_HOLDER_COUNT <= holders <= MAX_HOLDER_COUNT:
                base_score += 6

            risk_penalty = validation.get('risk_score', 0) * 0.22
            final_score = max(base_score - risk_penalty, 0)

            return float(min(final_score, 100))

        except Exception as e:
            logger.error(f"Signal strength calculation error: {e}")
            return 0

    def build_narrative(self, token: dict, validation: dict) -> str:
        fragments = []

        buy5m = token.get('buy5m') or 0
        buy1h = token.get('buy1h') or 0
        dominance = validation.get('buyer_dominance', 0)
        price_change_1h = token.get('price_change_1h') or 0
        price_change_5m = token.get('price_change_5m') or 0
        discovery = token.get('discovery_strategy')

        if buy5m >= 3:
            fragments.append('Fresh 5m buyers')
        elif buy5m >= 1:
            fragments.append('Recent buy pressure')

        if dominance >= 0.8:
            fragments.append('Buyer dominated')
        elif dominance >= 0.65:
            fragments.append('Strong buy wall')

        if price_change_1h >= 25:
            fragments.append('1h breakout momentum')
        elif price_change_1h >= 10:
            fragments.append('1h uptrend intact')
        elif price_change_1h < -5 and buy1h > 0:
            fragments.append('Dip buy inflow')

        if price_change_5m >= 5:
            fragments.append('5m spike')

        if discovery:
            fragments.append(discovery)

        if not fragments:
            return 'Early narrative forming'

        return ' | '.join(fragments[:3])

    def should_send_signal(self, token: dict, signal_strength: float, guard_stats: dict = None) -> tuple:
        """
        Determine if signal should be sent based on advanced criteria.
        Returns (pass: bool, rejection_reason: str)
        guard_stats is updated with counts per rejection reason if provided
        """
        try:
            symbol = token.get('symbol', '')
            holders = token.get('holders') or 0
            buy5m = token.get('buy5m') or 0
            buys_1h = token.get('buy1h') or 0
            buy24h = token.get('buy24h') or 0
            dominance = token.get('buyer_dominance') or 0
            momentum = token.get('momentum_score') or 0
            helius_wallets_1h = token.get('helius_unique_wallets_1h') or 0
            helius_buy_usd = float(token.get('helius_buy_volume_1h_usd') or 0)
            last_trade_minutes = token.get('last_trade_minutes') or token.get('helius_last_activity_minutes')
            price_change_1h = abs(token.get('v1hChangePercent') or 0)
            volume_ratio = token.get('volume_ratio') or 0

            # Check for obvious scam tokens
            scam_keywords = ['SCAM', 'RUG', 'FAKE', 'TEST', 'DEAD']
            if any(keyword in symbol.upper() for keyword in scam_keywords):
                logger.warning(f"Potential scam token detected: {symbol}")
                if guard_stats is not None:
                    guard_stats['scam_keyword'] = guard_stats.get('scam_keyword', 0) + 1
                return (False, 'scam_keyword')

            # Skip major tokens and stables
            major_tokens = ['SOL', 'USDC', 'USDT', 'BTC', 'ETH', 'WBTC', 'WETH']
            stable_coins = {'USDC', 'USDT', 'USDC.SO', 'USDC.E', 'USDC.S', 'UXD', 'DAI', 'USDH', 'PYUSD', 'USD1', 'USDS', 'USD'}
            upper_symbol = symbol.upper()
            if upper_symbol in major_tokens or upper_symbol in stable_coins:
                if guard_stats is not None:
                    guard_stats['major_token'] = guard_stats.get('major_token', 0) + 1
                return (False, 'major_token')

            if holders < MIN_HOLDER_COUNT or holders > MAX_HOLDER_COUNT:
                if guard_stats is not None:
                    guard_stats['holder_count'] = guard_stats.get('holder_count', 0) + 1
                return (False, 'holder_count')

            effective_buyers_1h = max(buys_1h, helius_wallets_1h)

            # RELAXED GATING: Allow strong Birdeye momentum even if Helius stale
            # Conditions: momentum ≥55, price_change_1h ≥8%, volume_ratio ≥0.35, dominance >0.35, buy24h ≥3
            helius_is_empty = (helius_wallets_1h == 0 and helius_buy_usd == 0)
            strong_birdeye_momentum = (
                momentum >= 55
                and price_change_1h >= 8
                and volume_ratio >= 0.35
                and dominance > 0.35
                and buy24h >= 3
            )

            if helius_is_empty and strong_birdeye_momentum:
                logger.info(f"{symbol}: Allowing signal with stale Helius but strong Birdeye (momentum={momentum:.1f}, Δ1h={price_change_1h:.1f}%, vol_ratio={volume_ratio:.2f})")
                return (True, None)

            # Standard gating path
            if dominance < self.dynamic_min_buyer_dominance and effective_buyers_1h < self.dynamic_min_buyers_1h and buy24h < self.dynamic_min_buyers_1h * 3:
                if guard_stats is not None:
                    guard_stats['low_dominance_buyers'] = guard_stats.get('low_dominance_buyers', 0) + 1
                return (False, 'low_dominance_buyers')

            if momentum < 20:
                if guard_stats is not None:
                    guard_stats['low_momentum'] = guard_stats.get('low_momentum', 0) + 1
                return (False, 'low_momentum')

            if last_trade_minutes is not None and last_trade_minutes > max(60, 30 + 5 * self.empty_cycles):
                if guard_stats is not None:
                    guard_stats['stale_trade'] = guard_stats.get('stale_trade', 0) + 1
                return (False, 'stale_trade')

            if effective_buyers_1h < self.dynamic_min_buyers_1h and buy5m == 0 and buy24h < self.dynamic_min_buyers_1h * 3:
                if guard_stats is not None:
                    guard_stats['insufficient_buyers'] = guard_stats.get('insufficient_buyers', 0) + 1
                return (False, 'insufficient_buyers')

            if helius_buy_usd and helius_buy_usd < 150:
                if guard_stats is not None:
                    guard_stats['low_helius_volume'] = guard_stats.get('low_helius_volume', 0) + 1
                return (False, 'low_helius_volume')

            return (True, None)

        except Exception as e:
            logger.error(f"Signal decision error: {e}")
            if guard_stats is not None:
                guard_stats['error'] = guard_stats.get('error', 0) + 1
            return (False, 'error')

    async def send_enhanced_signal(self, token: dict, signal_strength: float, validation: dict):
        """Send enhanced signal with risk information"""
        try:
            symbol = token.get('symbol', '')
            address = token.get('address', '')
            price = float(token.get('price') or 0)
            volume = float(token.get('v24hUSD') or 0)
            mcap = float(token.get('mc') or 0)
            change_raw = token.get('v24hChangePercent')
            change = float(change_raw) if change_raw is not None else 0.0
            strategy = token.get('discovery_strategy', 'Unknown')
            turnover = validation.get('volume_ratio', 0)

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

            holders = int(token.get('holders') or 0)
            buy1h = int(token.get('buy1h') or 0)
            buy5m = int(token.get('buy5m') or 0)
            dominance = validation.get('buyer_dominance', 0)
            dominance_pct = dominance * 100
            momentum_score = validation.get('momentum_score', 0)
            unique_1h = int(token.get('unique_wallets_1h') or 0)
            helius_wallets_1h = int(token.get('helius_unique_wallets_1h') or unique_1h)
            helius_buy_usd = float(token.get('helius_buy_volume_1h_usd') or 0)
            helius_tx_1h = int(token.get('helius_transactions_1h') or 0)
            narrative = self.build_narrative(token, validation)
            last_trade_minutes = validation.get('last_trade_minutes') or token.get('helius_last_activity_minutes')
            if last_trade_minutes is not None:
                last_trade_label = f"{last_trade_minutes:.0f}m ago"
            else:
                last_trade_label = "unknown"

            jupiter_link = f"https://jup.ag/swap/SOL-{address}"
            dexscreener_link = f"https://dexscreener.com/solana/{address}"
            pst_time = datetime.now(self.signal_timezone).strftime('%Y-%m-%d %I:%M:%S %p %Z')

            message = f"""{strength_emoji} <b>MOMENTUM SIGNAL</b> {strength_emoji}

💎 <b>Token:</b> ${symbol}
🧾 <b>Address:</b> <code>{address}</code>
🎯 <b>Signal Strength:</b> {signal_strength:.1f}/100
⚠️ <b>Risk Level:</b> {risk_level}

💰 <b>Price:</b> ${price:.8f}
📊 <b>24h Change:</b> {change:+.1f}%
💸 <b>Volume:</b> ${volume:,.0f}
🎯 <b>Market Cap:</b> ${mcap:,.0f}
👥 <b>Holders:</b> {holders}
🛒 <b>Buys:</b> 1h {buy1h} | 5m {buy5m}
🔥 <b>Buyer Dominance:</b> {dominance_pct:.0f}%
💥 <b>Momentum Score:</b> {momentum_score:.0f}/100
🔁 <b>Turnover:</b> {turnover:.2f}x
📈 <b>Volume Quality:</b> {validation['volume_quality']}/100
👤 <b>Active Wallets (1h):</b> {unique_1h}
🤝 <b>Helius Wallets (1h):</b> {helius_wallets_1h}
💵 <b>Helius Buy Vol (1h):</b> ${helius_buy_usd:,.0f}
🔄 <b>Helius Tx (1h):</b> {helius_tx_1h}
⏱️ <b>Last Trade:</b> {last_trade_label}
🧠 <b>Narrative:</b> {narrative}
🔍 <b>Discovery:</b> {strategy}

🔗 <b>Jupiter:</b> <a href="{jupiter_link}">Swap</a>
📊 <b>DexScreener:</b> <a href="{dexscreener_link}">Live Chart</a>

⏰ {pst_time}

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
                        sent_at = datetime.now()
                        self.sent_signals[address] = sent_at
                        self.signal_history.append({
                            'symbol': symbol,
                            'address': address,
                            'signal_strength': signal_strength,
                            'risk_score': risk_score,
                            'sent_time': sent_at.isoformat()
                        })
                        # Store in AURA database for dashboard
                        try:
                            import sqlite3
                            import json as json_module
                            conn = sqlite3.connect('aura.db')
                            cur = conn.cursor()

                            cur.execute("""
                                INSERT INTO helix_signals
                                (token_address, symbol, momentum_score, market_cap, liquidity, volume_24h, price, timestamp, metadata)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                address,
                                symbol,
                                signal_strength,
                                mcap,
                                token.get('liquidity', 0),
                                volume,
                                price,
                                datetime.now().isoformat(),
                                json_module.dumps({
                                    'risk_score': risk_score,
                                    'buyer_dominance': dominance,
                                    'narrative': narrative,
                                    'discovery': strategy
                                })
                            ))

                            conn.commit()
                            conn.close()
                            logger.info(f"✅ Stored signal in AURA database: {symbol}")
                        except Exception as db_error:
                            logger.error(f"Failed to store signal in database: {db_error}")

                        if len(self.signal_history) > 500:
                            self.signal_history = self.signal_history[-500:]

                        return True
                    else:
                        logger.error(f"Telegram error: HTTP {response.status}")

        except Exception as e:
            logger.error(f"Enhanced signal send error: {e}")

        return False

    async def run_scan_cycle(self):
        """Run a complete scan cycle"""
        try:
            cycle_start = time.time()
            logger.info("Starting scan cycle...")

            # Get market data
            tokens = self.get_market_data()
            if not tokens:
                logger.warning("No market data retrieved")
                return 0

            try:
                await asyncio.wait_for(self.enrich_token_metrics(tokens), timeout=60)
                logger.info(f"Enriched metrics for {len(tokens)} tokens")
            except asyncio.TimeoutError:
                logger.error("Token enrichment timed out after 60 seconds - continuing anyway")
            except Exception as e:
                logger.error(f"Token enrichment failed: {e} - continuing anyway")

            # Re-enabled Helius with improved timeout handling
            logger.info("Starting Helius activity fetch...")
            try:
                await asyncio.wait_for(self.fetch_helius_activity(tokens), timeout=45)
                logger.info(f"✅ Fetched Helius activity for {len(tokens)} tokens")
            except asyncio.TimeoutError:
                logger.warning("⏱️ Helius activity fetch timed out after 45 seconds - continuing with Birdeye data only")
            except Exception as e:
                logger.warning(f"⚠️ Helius activity fetch failed: {e} - continuing with Birdeye data only")

            logger.info("Starting token prioritization...")
            try:
                tokens = self.prioritize_wallet_activity(tokens)[:self.max_tokens]
                logger.info(f"Prioritized to {len(tokens)} tokens for analysis")
            except Exception as e:
                logger.error(f"Token prioritization failed: {e}")
                tokens = tokens[:self.max_tokens]
                logger.info(f"Using {len(tokens)} tokens without prioritization")

            signals_sent = 0
            processed_tokens = 0
            filter_stats = {
                'missing_address': 0,
                'duplicate': 0,
                'validation': 0,
                'weak': 0,
                'symbol_guard': 0,
                'additional_filters': 0,
                'watchlist': 0,
            }
            guard_stats = {}  # Track rejection reasons from should_send_signal

            for token in tokens:
                try:
                    processed_tokens += 1
                    symbol = token.get('symbol', 'UNKNOWN')
                    address = token.get('address')

                    # Skip obvious non-tokens
                    if not symbol or len(symbol) > 20:
                        filter_stats['symbol_guard'] += 1
                        continue

                    if not address:
                        filter_stats['missing_address'] += 1
                        continue

                    if self.has_recent_signal(address):
                        filter_stats['duplicate'] += 1
                        continue

                    # Advanced volume validation
                    validation = self.advanced_volume_validation(token)
                    tentative_strength = self.calculate_signal_strength(token, validation)
                    if not validation['is_valid']:
                        if self.should_watchlist(token, validation, tentative_strength, 'validation gate'):
                            if await self.send_watchlist_signal(token, tentative_strength, validation, 'validation gate'):
                                filter_stats['watchlist'] += 1
                        filter_stats['validation'] += 1
                        continue

                    token['buyer_dominance'] = validation.get('buyer_dominance', 0)
                    token['momentum_score'] = validation.get('momentum_score', 0)
                    token['last_trade_minutes'] = validation.get('last_trade_minutes')

                    signal_strength = tentative_strength

                    if signal_strength < self.signal_threshold:
                        if self.should_watchlist(token, validation, signal_strength, 'below threshold'):
                            if await self.send_watchlist_signal(token, signal_strength, validation, 'below threshold'):
                                filter_stats['watchlist'] += 1
                        filter_stats['weak'] += 1
                        continue

                    # Call updated should_send_signal with guard_stats tracking
                    token['volume_ratio'] = validation.get('volume_ratio', 0)
                    should_send, rejection_reason = self.should_send_signal(token, signal_strength, guard_stats)

                    if should_send:
                        success = await self.send_enhanced_signal(token, signal_strength, validation)
                        if success:
                            signals_sent += 1
                            await asyncio.sleep(3)  # Rate limiting between signals
                    else:
                        if self.should_watchlist(token, validation, signal_strength, f'additional filters ({rejection_reason})'):
                            if await self.send_watchlist_signal(token, signal_strength, validation, f'additional filters ({rejection_reason})'):
                                filter_stats['watchlist'] += 1
                        filter_stats['additional_filters'] += 1


                except Exception as e:
                    logger.error(f"Token processing error: {e}")
                    continue

            cycle_duration = time.time() - cycle_start
            self.adjust_adaptive_thresholds(signals_sent)
            self.record_cycle_metrics(signals_sent, filter_stats, cycle_duration)

            # Append guard_stats to filter_stats for comprehensive logging
            filter_stats.update(guard_stats)

            guard_summary = " | ".join(f"{k}:{v}" for k, v in guard_stats.items() if v > 0) if guard_stats else "none"
            logger.info(
                "Scan complete: %d processed, %d signals sent | filters -> validation:%d weak:%d duplicates:%d missing:%d symbol:%d other:%d watch:%d | guards -> %s (%.2fs)",
                processed_tokens,
                signals_sent,
                filter_stats['validation'],
                filter_stats['weak'],
                filter_stats['duplicate'],
                filter_stats['missing_address'],
                filter_stats['symbol_guard'],
                filter_stats['additional_filters'],
                filter_stats['watchlist'],
                guard_summary,
                cycle_duration,
            )
            return signals_sent

        except Exception as e:
            logger.error(f"Scan cycle error: {e}")
            return 0

    async def ensure_graduation_background(self):
        """Initialize graduation system using Helius/Birdeye data (no Pump.fun scraping)"""
        if not grad_cfg or not getattr(grad_cfg, "enabled", False):
            return
        if self.graduation_task and not self.graduation_task.done():
            return

        if bootstrap_detectors:
            try:
                await bootstrap_detectors()
                logger.info("Graduation detectors bootstrapped at %s", datetime.now(ZoneInfo("UTC")).isoformat())
            except Exception as exc:
                logger.debug("Graduation bootstrap failed: %s", exc)

    async def run_continuous_scanner(self):
        """Run continuous momentum scanning"""
        logger.info("Starting continuous momentum scanner...")

        while True:
            try:
                try:
                    await self.ensure_graduation_background()
                except Exception as exc:
                    logger.debug("Graduation background startup failed: %s", exc)

                current_time = time.time()

                # Check scan interval
                if current_time - self.last_scan_time >= self.min_scan_interval:
                    try:
                        signals_sent = await self.run_scan_cycle()
                        self.last_scan_time = current_time

                        self.prune_sent_signals()
                        self.prune_watchlist_sent()
                        self.prune_helius_cache()

                        # Status update
                        if signals_sent > 0:
                            logger.info(f"✅ Sent {signals_sent} signals this cycle")
                        else:
                            logger.info("⏳ No qualifying signals found - continuing monitoring")
                    except Exception as e:
                        logger.error(f"Scan cycle error: {e} - continuing to next cycle")
                        self.last_scan_time = current_time  # Prevent immediate retry

                await asyncio.sleep(60)  # Check every minute

            except KeyboardInterrupt:
                logger.info("Scanner stopped by user")
                break
            except Exception as e:
                logger.error(f"Scanner error: {e} - restarting loop")

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
