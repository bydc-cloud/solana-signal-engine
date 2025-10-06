#!/usr/bin/env python3
"""Initialize database with minimal required tables"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "final_nuclear.db"

def init_database():
    """Create minimal required tables"""
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()

        # Create alerts table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_address TEXT NOT NULL,
                symbol TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                grad_gs REAL,
                payload TEXT
            )
        """)

        # Create trades table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_address TEXT,
                symbol TEXT,
                side TEXT,
                amount_usd REAL,
                price REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create grad_paper_equity table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS grad_paper_equity (
                id INTEGER PRIMARY KEY,
                equity_usd REAL DEFAULT 100000,
                realized_pnl_usd REAL DEFAULT 0,
                unrealized_pnl_usd REAL DEFAULT 0,
                ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert default paper equity if not exists
        cur.execute("""
            INSERT OR IGNORE INTO grad_paper_equity (id, equity_usd, realized_pnl_usd, unrealized_pnl_usd, ts)
            VALUES (1, 100000, 0, 0, CURRENT_TIMESTAMP)
        """)

        conn.commit()
        print(f"✅ Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_database()
