"""
Performance Configuration for 100x Optimization
- Connection pooling
- Query caching
- Async operations
- Memory management
"""
from functools import lru_cache
from datetime import datetime, timedelta
import asyncio

class PerformanceConfig:
    """Performance settings"""

    # Database
    DB_CONNECTION_POOL_SIZE = 20
    DB_QUERY_CACHE_SIZE = 1000
    DB_QUERY_CACHE_TTL = 60  # seconds

    # API
    API_WORKER_COUNT = 4
    API_MAX_CONCURRENT_REQUESTS = 100
    API_TIMEOUT = 30

    # Voice
    VOICE_RESPONSE_CACHE_SIZE = 50
    VOICE_MAX_TOKENS = 300  # Faster responses

    # Signals
    SIGNALS_BATCH_SIZE = 100
    SIGNALS_UPDATE_INTERVAL = 5  # seconds

    # Wallets
    WALLET_BATCH_SIZE = 20
    WALLET_UPDATE_INTERVAL = 30  # seconds
    WALLET_CONCURRENT_UPDATES = 10

    # Cache
    CACHE_ENABLED = True
    CACHE_TTL_SIGNALS = 30
    CACHE_TTL_WALLETS = 60
    CACHE_TTL_PORTFOLIO = 120

# Global cache
_cache = {}
_cache_timestamps = {}

def get_cached(key: str, ttl: int = 60):
    """Get cached value if not expired"""
    if not PerformanceConfig.CACHE_ENABLED:
        return None

    if key in _cache:
        timestamp = _cache_timestamps.get(key)
        if timestamp and (datetime.now() - timestamp).seconds < ttl:
            return _cache[key]
    return None

def set_cached(key: str, value, ttl: int = 60):
    """Set cached value"""
    if not PerformanceConfig.CACHE_ENABLED:
        return

    _cache[key] = value
    _cache_timestamps[key] = datetime.now()

def clear_cache(pattern: str = None):
    """Clear cache by pattern or all"""
    global _cache, _cache_timestamps
    if pattern:
        keys_to_delete = [k for k in _cache.keys() if pattern in k]
        for k in keys_to_delete:
            del _cache[k]
            del _cache_timestamps[k]
    else:
        _cache.clear()
        _cache_timestamps.clear()
