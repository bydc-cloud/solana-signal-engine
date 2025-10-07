#!/bin/bash

echo "🚀 DEPLOYING COMPLETE AURA SYSTEM..."

# 1. Initialize all databases
echo "📊 Initializing databases..."
python3 init_aura_db.py

# 2. Create helix_signals table if missing
echo "📡 Creating signals table..."
sqlite3 aura.db <<EOF
CREATE TABLE IF NOT EXISTS helix_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token_address TEXT NOT NULL,
    symbol TEXT,
    momentum_score REAL,
    market_cap REAL,
    liquidity REAL,
    volume_24h REAL,
    price REAL,
    timestamp TEXT,
    metadata TEXT
);
CREATE INDEX IF NOT EXISTS idx_helix_signals_timestamp ON helix_signals(timestamp);
CREATE INDEX IF NOT EXISTS idx_helix_signals_token ON helix_signals(token_address);
EOF

# 3. Discover and track top wallets
echo "🐋 Discovering top wallets..."
python3 << 'PYTHON'
import asyncio
from aura.whale_tracker import whale_tracker

async def discover():
    wallets = await whale_tracker.discover_top_wallets(limit=100)
    print(f"✅ Discovered {len(wallets)} top wallets")

asyncio.run(discover())
PYTHON

# 4. Commit and push
echo "📦 Committing changes..."
git add -A
git commit -m "fix: Complete AURA deployment with data

- Initialize all database tables
- Create helix_signals table
- Discover top 100 wallets
- Ready for live signals

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git push origin main

# 5. Deploy to Railway
echo "🚂 Deploying to Railway..."
railway up --detach

echo "✅ DEPLOYMENT COMPLETE!"
echo "🌐 Dashboard: https://signal-railway-deployment-production.up.railway.app/"
echo "📡 Signals will appear as scanner runs"
echo "🐋 Wallets tab now populated with top performers"
EOF
chmod +x DEPLOY_COMPLETE_AURA.sh
