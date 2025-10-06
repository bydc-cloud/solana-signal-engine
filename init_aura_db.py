#!/usr/bin/env python3
"""
AURA Database Initialization Script
Creates all required tables for the AURA autonomous crypto intelligence system
"""
import sqlite3
from pathlib import Path
from datetime import datetime

AURA_DB_PATH = Path(__file__).parent / "aura.db"

def init_aura_database():
    """Initialize AURA database with all required tables"""
    print("🚀 Initializing AURA database...")

    with sqlite3.connect(AURA_DB_PATH) as conn:
        cur = conn.cursor()

        # ═══════════════════════════════════════════════════════════
        # TOKEN KNOWLEDGE BASE
        # ═══════════════════════════════════════════════════════════

        print("📊 Creating tokens table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tokens (
                address TEXT PRIMARY KEY,
                symbol TEXT,
                name TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,  -- JSON: {mc, liquidity, holders, price, etc}
                risk_score REAL DEFAULT 0.5,  -- 0-1 scale
                sentiment_score REAL DEFAULT 0.5  -- 0-1 scale
            )
        """)

        print("📝 Creating token_facts table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS token_facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_address TEXT NOT NULL,
                fact_type TEXT NOT NULL,  -- 'technical', 'social', 'fundamental', 'security'
                fact TEXT NOT NULL,
                source TEXT NOT NULL,  -- 'birdeye', 'twitter', 'defillama', 'rugcheck'
                confidence REAL DEFAULT 0.8,  -- 0-1 scale
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,  -- NULL for permanent facts
                FOREIGN KEY (token_address) REFERENCES tokens(address)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_token_facts_address ON token_facts(token_address)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_token_facts_type ON token_facts(fact_type)")

        # ═══════════════════════════════════════════════════════════
        # USER SYSTEM
        # ═══════════════════════════════════════════════════════════

        print("👤 Creating user_profiles table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT DEFAULT 'User',
                risk_tolerance TEXT DEFAULT 'moderate',  -- 'conservative', 'moderate', 'aggressive'
                preferences TEXT,  -- JSON: {max_position_size_usd, max_portfolio_exposure, etc}
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert default user if not exists
        cur.execute("""
            INSERT OR IGNORE INTO user_profiles (id, name, risk_tolerance, preferences)
            VALUES (1, 'Default User', 'moderate', '{"max_position_size_usd": 1000, "max_portfolio_exposure": 0.2}')
        """)

        # ═══════════════════════════════════════════════════════════
        # PORTFOLIO MANAGEMENT
        # ═══════════════════════════════════════════════════════════

        print("💼 Creating portfolio_items table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS portfolio_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                token_address TEXT NOT NULL,
                entry_price REAL NOT NULL,
                amount REAL NOT NULL,
                entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                exit_price REAL,
                exit_time TIMESTAMP,
                pnl_usd REAL DEFAULT 0,
                pnl_percent REAL DEFAULT 0,
                status TEXT DEFAULT 'open',  -- 'open', 'closed'
                notes TEXT,  -- Why entered, strategy used, etc
                FOREIGN KEY (user_id) REFERENCES user_profiles(id),
                FOREIGN KEY (token_address) REFERENCES tokens(address)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_portfolio_status ON portfolio_items(status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_portfolio_user ON portfolio_items(user_id)")

        print("👁️ Creating watchlist table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                token_address TEXT NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reason TEXT,  -- Why watching
                alert_rules TEXT,  -- JSON: {price_change_percent: 10, volume_spike_ratio: 2.0, momentum_threshold: 70}
                triggered_count INTEGER DEFAULT 0,
                last_triggered TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_profiles(id),
                FOREIGN KEY (token_address) REFERENCES tokens(address),
                UNIQUE(user_id, token_address)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_watchlist_user ON watchlist(user_id)")

        # ═══════════════════════════════════════════════════════════
        # STRATEGY SYSTEM
        # ═══════════════════════════════════════════════════════════

        print("🎯 Creating strategies table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS strategies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                type TEXT NOT NULL,  -- 'momentum', 'mean_reversion', 'breakout', 'contrarian'
                rules TEXT NOT NULL,  -- JSON: {entry: {momentum >= 70, volume_ratio >= 0.5}, exit: {pnl_percent <= -5 OR pnl_percent >= 20}}
                capital_allocation_usd REAL DEFAULT 5000,
                status TEXT DEFAULT 'active',  -- 'active', 'paused', 'backtesting', 'archived'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metrics TEXT  -- JSON: {total_trades, win_rate, avg_pnl, sharpe_ratio, max_drawdown}
            )
        """)

        print("📈 Creating strategy_trades table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS strategy_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_id INTEGER NOT NULL,
                token_address TEXT NOT NULL,
                side TEXT NOT NULL,  -- 'buy', 'sell'
                price REAL NOT NULL,
                amount REAL NOT NULL,
                amount_usd REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                pnl_usd REAL DEFAULT 0,
                pnl_percent REAL DEFAULT 0,
                reason TEXT,  -- Why this trade was made
                FOREIGN KEY (strategy_id) REFERENCES strategies(id),
                FOREIGN KEY (token_address) REFERENCES tokens(address)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_strategy_trades_strategy ON strategy_trades(strategy_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_strategy_trades_timestamp ON strategy_trades(timestamp)")

        # Insert example strategies
        cur.execute("""
            INSERT OR IGNORE INTO strategies (id, name, description, type, rules, capital_allocation_usd, metrics)
            VALUES (
                1,
                'High Momentum Scanner',
                'Buys tokens with momentum >= 70 and strong volume',
                'momentum',
                '{"entry": {"momentum": {"gte": 70}, "volume_ratio": {"gte": 0.5}, "buy_volume_1h_usd": {"gte": 500}}, "exit": {"pnl_percent_target": 25, "stop_loss_percent": -8, "time_limit_minutes": 240}}',
                5000,
                '{"total_trades": 0, "win_rate": 0, "avg_pnl": 0, "max_drawdown": 0}'
            )
        """)

        # ═══════════════════════════════════════════════════════════
        # ALERT SYSTEM
        # ═══════════════════════════════════════════════════════════

        print("🔔 Creating alert_configs table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS alert_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                name TEXT NOT NULL,
                description TEXT,
                conditions TEXT NOT NULL,  -- JSON: {momentum: {gte: 70}, volume_ratio: {gte: 0.5}}
                actions TEXT NOT NULL,  -- JSON: {notify: true, auto_add_watchlist: true, auto_execute_strategy: 1}
                enabled BOOLEAN DEFAULT 1,
                priority TEXT DEFAULT 'medium',  -- 'low', 'medium', 'high', 'critical'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_profiles(id)
            )
        """)

        print("📜 Creating alert_history table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS alert_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_id INTEGER,
                token_address TEXT NOT NULL,
                triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message TEXT NOT NULL,
                priority TEXT DEFAULT 'medium',
                read BOOLEAN DEFAULT 0,
                metadata TEXT,  -- JSON: token details at trigger time
                FOREIGN KEY (config_id) REFERENCES alert_configs(id),
                FOREIGN KEY (token_address) REFERENCES tokens(address)
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_alert_history_read ON alert_history(read)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_alert_history_triggered ON alert_history(triggered_at)")

        # Insert default alert configs
        cur.execute("""
            INSERT OR IGNORE INTO alert_configs (id, name, description, conditions, actions, priority)
            VALUES (
                1,
                'High Momentum Signal',
                'Alert when scanner finds high momentum token',
                '{"momentum": {"gte": 70}, "volume_ratio": {"gte": 0.5}}',
                '{"notify": true, "auto_add_watchlist": true}',
                'high'
            )
        """)

        # ═══════════════════════════════════════════════════════════
        # CONFIGURATION
        # ═══════════════════════════════════════════════════════════

        print("⚙️ Creating system_configs table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS system_configs (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert default configs
        default_configs = [
            ('paper_trading_enabled', 'true', 'Enable/disable paper trading'),
            ('max_concurrent_positions', '5', 'Maximum open positions at once'),
            ('default_position_size_usd', '1000', 'Default trade size'),
            ('risk_per_trade_percent', '2', 'Max risk per trade (% of portfolio)'),
            ('scanner_signal_threshold', '65', 'Minimum momentum score for signals'),
            ('auto_watchlist_enabled', 'true', 'Auto-add strong signals to watchlist'),
            ('telegram_notifications', 'false', 'Send alerts to Telegram'),
            ('dashboard_refresh_seconds', '30', 'Dashboard auto-refresh interval'),
        ]

        for key, value, desc in default_configs:
            cur.execute("""
                INSERT OR IGNORE INTO system_configs (key, value, description)
                VALUES (?, ?, ?)
            """, (key, value, desc))

        # ═══════════════════════════════════════════════════════════
        # MEMORY SYSTEM (Lightweight - MCP memory for heavy lifting)
        # ═══════════════════════════════════════════════════════════

        print("🧠 Creating aura_memories table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS aura_memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_name TEXT NOT NULL,
                entity_type TEXT NOT NULL,  -- 'token', 'strategy', 'user_preference', 'pattern'
                observations TEXT NOT NULL,  -- JSON array of observations
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                last_accessed TIMESTAMP
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_memories_entity ON aura_memories(entity_name)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_memories_type ON aura_memories(entity_type)")

        # ═══════════════════════════════════════════════════════════
        # ANALYTICS & METRICS
        # ═══════════════════════════════════════════════════════════

        print("📊 Creating daily_metrics table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS daily_metrics (
                date DATE PRIMARY KEY,
                portfolio_value_usd REAL,
                daily_pnl_usd REAL,
                daily_pnl_percent REAL,
                total_trades INTEGER,
                winning_trades INTEGER,
                signals_generated INTEGER,
                alerts_triggered INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ═══════════════════════════════════════════════════════════
        # DASHBOARD-SPECIFIC TABLES (for dashboard API)
        # ═══════════════════════════════════════════════════════════

        print("🔔 Creating alerts table (dashboard)...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_address TEXT,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'unread',
                alert_config_id INTEGER,
                metadata_json TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                read_at TEXT,
                dismissed_at TEXT
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_alerts_token ON alerts(token_address)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status)")

        print("💰 Creating trades table (dashboard)...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_address TEXT NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                price REAL NOT NULL,
                amount REAL NOT NULL,
                value_usd REAL NOT NULL,
                status TEXT DEFAULT 'active',
                entry_price REAL,
                exit_price REAL,
                pnl_usd REAL DEFAULT 0,
                pnl_percent REAL DEFAULT 0,
                strategy_id INTEGER,
                notes TEXT,
                metadata_json TEXT,
                opened_at TEXT DEFAULT (datetime('now')),
                closed_at TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_trades_token ON trades(token_address)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status)")

        conn.commit()
        print("✅ AURA database initialized successfully!")
        print(f"📍 Location: {AURA_DB_PATH}")

        # Print table counts
        tables = [
            'tokens', 'token_facts', 'user_profiles', 'portfolio_items',
            'watchlist', 'strategies', 'strategy_trades', 'alert_configs',
            'alert_history', 'system_configs', 'aura_memories', 'daily_metrics',
            'alerts', 'trades'
        ]

        print("\n📋 Table Summary:")
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            print(f"   • {table}: {count} rows")

if __name__ == "__main__":
    init_aura_database()
