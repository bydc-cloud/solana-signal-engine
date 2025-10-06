-- ════════════════════════════════════════════════════════════════════════════
-- AURA Dashboard Foundation - Database Migrations
-- Version: 001
-- Author: AURA v0.2.1
-- Date: 2025-10-06
-- ════════════════════════════════════════════════════════════════════════════

-- ═══════════════════════════════════════════════════════════
-- TOKENS TABLE
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    address TEXT NOT NULL UNIQUE,
    symbol TEXT NOT NULL,
    name TEXT NOT NULL,
    decimals INTEGER DEFAULT 9,
    logo_uri TEXT,
    metadata_json TEXT,  -- JSON: mc, liquidity, holders, etc.
    coingecko_id TEXT,
    coingecko_rank INTEGER,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_tokens_address ON tokens(address);
CREATE INDEX IF NOT EXISTS idx_tokens_symbol ON tokens(symbol);
CREATE INDEX IF NOT EXISTS idx_tokens_coingecko_id ON tokens(coingecko_id);

-- ═══════════════════════════════════════════════════════════
-- TOKEN PRICE OHLC (Time-series data)
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS token_price_ohlc (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token_address TEXT NOT NULL,
    timeframe TEXT NOT NULL,  -- '1m', '5m', '15m', '1h', '4h', '1d'
    timestamp INTEGER NOT NULL,  -- Unix timestamp
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    volume_usd REAL DEFAULT 0,
    trades_count INTEGER DEFAULT 0,
    source TEXT DEFAULT 'birdeye',  -- 'birdeye', 'dexscreener', 'helius'
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(token_address, timeframe, timestamp)
);

CREATE INDEX IF NOT EXISTS idx_ohlc_token_time ON token_price_ohlc(token_address, timeframe, timestamp);
CREATE INDEX IF NOT EXISTS idx_ohlc_timestamp ON token_price_ohlc(timestamp);

-- ═══════════════════════════════════════════════════════════
-- TOKEN TVL (Total Value Locked)
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS token_tvl (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token_address TEXT NOT NULL,
    tvl_usd REAL NOT NULL,
    liquidity_usd REAL DEFAULT 0,
    liquidity_pools INTEGER DEFAULT 0,
    timestamp INTEGER NOT NULL,  -- Unix timestamp
    source TEXT DEFAULT 'defillama',  -- 'defillama', 'birdeye'
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(token_address, timestamp, source)
);

CREATE INDEX IF NOT EXISTS idx_tvl_token_time ON token_tvl(token_address, timestamp);

-- ═══════════════════════════════════════════════════════════
-- TOKEN FACTS (Knowledge base)
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS token_facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token_address TEXT NOT NULL,
    fact_type TEXT NOT NULL,  -- 'technical', 'social', 'market', 'fundamental'
    fact TEXT NOT NULL,
    source TEXT NOT NULL,  -- 'helix_scanner', 'coingecko_mcp', 'firecrawl_mcp', etc.
    confidence REAL DEFAULT 0.8,  -- 0.0 to 1.0
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_facts_token ON token_facts(token_address);
CREATE INDEX IF NOT EXISTS idx_facts_type ON token_facts(fact_type);
CREATE INDEX IF NOT EXISTS idx_facts_source ON token_facts(source);

-- ═══════════════════════════════════════════════════════════
-- TRADES (Paper & Live Trading)
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token_address TEXT NOT NULL,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL,  -- 'buy', 'sell'
    price REAL NOT NULL,
    amount REAL NOT NULL,
    value_usd REAL NOT NULL,
    status TEXT DEFAULT 'active',  -- 'active', 'closed'
    entry_price REAL,
    exit_price REAL,
    pnl_usd REAL DEFAULT 0,
    pnl_percent REAL DEFAULT 0,
    strategy_id INTEGER,
    notes TEXT,
    metadata_json TEXT,  -- JSON: slippage, fees, etc.
    opened_at TEXT DEFAULT (datetime('now')),
    closed_at TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_trades_token ON trades(token_address);
CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status);
CREATE INDEX IF NOT EXISTS idx_trades_strategy ON trades(strategy_id);
CREATE INDEX IF NOT EXISTS idx_trades_opened ON trades(opened_at);

-- ═══════════════════════════════════════════════════════════
-- STRATEGIES (Trading Strategies)
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS strategies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL,  -- 'momentum', 'mean_reversion', 'breakout', etc.
    description TEXT,
    rules_json TEXT NOT NULL,  -- JSON: entry/exit rules
    enabled INTEGER DEFAULT 1,
    capital_allocation_usd REAL DEFAULT 1000,
    max_positions INTEGER DEFAULT 3,
    risk_per_trade_percent REAL DEFAULT 2.0,
    stats_json TEXT,  -- JSON: win_rate, total_pnl, trades_count, etc.
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_strategies_enabled ON strategies(enabled);
CREATE INDEX IF NOT EXISTS idx_strategies_type ON strategies(type);

-- ═══════════════════════════════════════════════════════════
-- ALERTS (System Alerts & Notifications)
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token_address TEXT,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    priority TEXT DEFAULT 'medium',  -- 'low', 'medium', 'high', 'critical'
    status TEXT DEFAULT 'unread',  -- 'unread', 'read', 'dismissed'
    alert_config_id INTEGER,
    metadata_json TEXT,  -- JSON: additional context
    created_at TEXT DEFAULT (datetime('now')),
    read_at TEXT,
    dismissed_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_alerts_token ON alerts(token_address);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_priority ON alerts(priority);
CREATE INDEX IF NOT EXISTS idx_alerts_created ON alerts(created_at);

-- ═══════════════════════════════════════════════════════════
-- ALERT CONFIGS (Alert Rules)
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS alert_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    conditions_json TEXT NOT NULL,  -- JSON: momentum >= X, volume_ratio >= Y
    actions_json TEXT NOT NULL,  -- JSON: notify, auto_add_watchlist
    priority TEXT DEFAULT 'medium',
    enabled INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_alert_configs_enabled ON alert_configs(enabled);

-- ═══════════════════════════════════════════════════════════
-- CONFIGS (System Configuration)
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    value TEXT NOT NULL,
    value_type TEXT DEFAULT 'string',  -- 'string', 'int', 'float', 'bool', 'json'
    description TEXT,
    version INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_configs_key ON configs(key);

-- ═══════════════════════════════════════════════════════════
-- CONFIG PATCHES (Configuration History & Rollback)
-- ═══════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS config_patches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_key TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT NOT NULL,
    patch_type TEXT DEFAULT 'update',  -- 'create', 'update', 'delete'
    applied INTEGER DEFAULT 0,  -- 0 = pending, 1 = applied
    approved_by TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    applied_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_patches_key ON config_patches(config_key);
CREATE INDEX IF NOT EXISTS idx_patches_applied ON config_patches(applied);
CREATE INDEX IF NOT EXISTS idx_patches_created ON config_patches(created_at);

-- ════════════════════════════════════════════════════════════════════════════
-- END OF MIGRATIONS
-- ════════════════════════════════════════════════════════════════════════════
--
-- ROLLBACK NOTES:
-- To rollback this migration, run:
--   DROP TABLE IF EXISTS config_patches;
--   DROP TABLE IF EXISTS configs;
--   DROP TABLE IF EXISTS alert_configs;
--   DROP TABLE IF EXISTS alerts;
--   DROP TABLE IF EXISTS strategies;
--   DROP TABLE IF EXISTS trades;
--   DROP TABLE IF EXISTS token_facts;
--   DROP TABLE IF EXISTS token_tvl;
--   DROP TABLE IF EXISTS token_price_ohlc;
--   DROP TABLE IF EXISTS tokens;
--
-- ════════════════════════════════════════════════════════════════════════════
