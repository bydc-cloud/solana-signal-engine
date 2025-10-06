"""
AURA API Endpoints
Complete REST API for autonomous crypto intelligence system
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime

from .database import db

router = APIRouter()

# ═══════════════════════════════════════════════════════════
# PYDANTIC MODELS
# ═══════════════════════════════════════════════════════════

class TokenCreate(BaseModel):
    address: str
    symbol: str
    name: str
    metadata: Dict

class PositionCreate(BaseModel):
    token_address: str
    entry_price: float
    amount: float
    notes: str = ""

class PositionClose(BaseModel):
    exit_price: float

class WatchlistAdd(BaseModel):
    token_address: str
    reason: str
    alert_rules: Dict = {}

class AlertCreate(BaseModel):
    token_address: str
    message: str
    priority: str = "medium"
    metadata: Optional[Dict] = None

class ConfigUpdate(BaseModel):
    key: str
    value: Any

# ═══════════════════════════════════════════════════════════
# PORTFOLIO ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.get("/portfolio")
async def get_portfolio(user_id: int = 1):
    """Get all portfolio positions and summary"""
    try:
        open_positions = db.get_open_positions(user_id)
        summary = db.get_portfolio_summary(user_id)

        # Enrich positions with token data
        for position in open_positions:
            token = db.get_token(position["token_address"])
            if token:
                position["symbol"] = token["symbol"]
                position["name"] = token["name"]

        return {
            "open_positions": open_positions,
            "summary": summary,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portfolio/{address}")
async def get_position_details(address: str):
    """Get detailed information about a specific position"""
    try:
        # Get token info
        token = db.get_token(address)
        if not token:
            raise HTTPException(status_code=404, detail="Token not found")

        # Get token facts
        facts = db.get_token_facts(address)

        # Get position history (all trades for this token)
        with db._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, entry_price, amount, entry_time, exit_price, exit_time, pnl_usd, pnl_percent, status
                FROM portfolio_items
                WHERE token_address = ?
                ORDER BY entry_time DESC
            """, (address,))

            positions = []
            for row in cur.fetchall():
                positions.append({
                    "id": row[0],
                    "entry_price": row[1],
                    "amount": row[2],
                    "entry_time": row[3],
                    "exit_price": row[4],
                    "exit_time": row[5],
                    "pnl_usd": row[6],
                    "pnl_percent": row[7],
                    "status": row[8],
                })

        return {
            "token": token,
            "facts": facts,
            "positions": positions,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/portfolio")
async def open_position(position: PositionCreate):
    """Open a new position"""
    try:
        position_id = db.add_position(
            position.token_address,
            position.entry_price,
            position.amount,
            position.notes
        )
        return {"id": position_id, "status": "open"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/portfolio/{position_id}/close")
async def close_position(position_id: int, close_data: PositionClose):
    """Close an existing position"""
    try:
        db.close_position(position_id, close_data.exit_price)
        return {"id": position_id, "status": "closed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/portfolio/simulate")
async def simulate_trade(position: PositionCreate):
    """Simulate trade impact without executing"""
    try:
        amount_usd = position.entry_price * position.amount

        # Get current portfolio value
        summary = db.get_portfolio_summary()
        total_value = summary["open_value_usd"] + 100000  # Assume 100k base

        position_size_percent = (amount_usd / total_value) * 100
        risk_per_trade = db.get_config("risk_per_trade_percent", 2)

        return {
            "amount_usd": amount_usd,
            "position_size_percent": position_size_percent,
            "within_risk_limit": position_size_percent <= risk_per_trade,
            "recommended_amount": (total_value * risk_per_trade / 100) / position.entry_price,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# WATCHLIST ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.get("/watchlist")
async def get_watchlist(user_id: int = 1):
    """Get all watched tokens"""
    try:
        watchlist = db.get_watchlist(user_id)

        # Enrich with token data
        for item in watchlist:
            token = db.get_token(item["token_address"])
            if token:
                item["symbol"] = token["symbol"]
                item["name"] = token["name"]
                item["metadata"] = token["metadata"]

        return {"watchlist": watchlist, "count": len(watchlist)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/watchlist")
async def add_to_watchlist(item: WatchlistAdd, user_id: int = 1):
    """Add token to watchlist"""
    try:
        db.add_to_watchlist(item.token_address, item.reason, item.alert_rules, user_id)
        return {"status": "added", "token_address": item.token_address}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/watchlist/{address}")
async def remove_from_watchlist(address: str, user_id: int = 1):
    """Remove token from watchlist"""
    try:
        db.remove_from_watchlist(address, user_id)
        return {"status": "removed", "token_address": address}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/watchlist/{address}")
async def update_watchlist_rules(address: str, alert_rules: Dict, user_id: int = 1):
    """Update alert rules for watched token"""
    try:
        # Update alert rules
        with db._get_conn() as conn:
            cur = conn.cursor()
            import json
            cur.execute("""
                UPDATE watchlist
                SET alert_rules = ?
                WHERE user_id = ? AND token_address = ?
            """, (json.dumps(alert_rules), user_id, address))
            conn.commit()

        return {"status": "updated", "token_address": address}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# TOKEN INTELLIGENCE ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.get("/tokens/{address}")
async def get_token_details(address: str):
    """Get comprehensive token details with facts"""
    try:
        token = db.get_token(address)
        if not token:
            raise HTTPException(status_code=404, detail="Token not found")

        facts = db.get_token_facts(address)

        # Get latest Helix signal if exists
        signals = db.get_recent_helix_signals(hours=168, limit=1000)  # Last week
        token_signals = [s for s in signals if s["token_address"] == address]

        return {
            "token": token,
            "facts": facts,
            "recent_signals": token_signals[:5],  # Last 5 signals
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tokens/{address}/similar")
async def find_similar_tokens(address: str, limit: int = 10):
    """Find tokens similar to this one based on characteristics"""
    try:
        token = db.get_token(address)
        if not token:
            raise HTTPException(status_code=404, detail="Token not found")

        # Simple similarity: same market cap range
        metadata = token.get("metadata", {})
        mc = metadata.get("mc", 0)

        if mc == 0:
            return {"similar_tokens": [], "count": 0}

        mc_min = mc * 0.5
        mc_max = mc * 2.0

        # Find tokens in similar MC range
        with db._get_conn() as conn:
            cur = conn.cursor()
            import json
            cur.execute("""
                SELECT address, symbol, name, metadata
                FROM tokens
                WHERE address != ?
                LIMIT ?
            """, (address, limit))

            similar = []
            for row in cur.fetchall():
                try:
                    meta = json.loads(row[3]) if row[3] else {}
                    token_mc = meta.get("mc", 0)
                    if mc_min <= token_mc <= mc_max:
                        similar.append({
                            "address": row[0],
                            "symbol": row[1],
                            "name": row[2],
                            "mc": token_mc,
                        })
                except:
                    continue

        return {"similar_tokens": similar[:limit], "count": len(similar)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tokens/{address}/analyze")
async def deep_analyze_token(address: str):
    """Trigger deep analysis of token (enrichment via MCPs)"""
    try:
        # This would trigger async job to:
        # 1. Fetch from DeFiLlama
        # 2. Check RugCheck
        # 3. Scrape Twitter sentiment
        # 4. Analyze holder distribution
        # For now, return placeholder
        return {
            "status": "analysis_started",
            "token_address": address,
            "estimated_completion": "30 seconds",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# STRATEGY ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.get("/strategies")
async def list_strategies():
    """List all strategies"""
    try:
        strategies = db.get_active_strategies()
        return {"strategies": strategies, "count": len(strategies)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/strategies/{strategy_id}/backtest")
async def backtest_strategy(strategy_id: int, days: int = 30):
    """Get backtest results for strategy"""
    try:
        # Get strategy trades
        with db._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT side, price, amount_usd, timestamp, pnl_usd
                FROM strategy_trades
                WHERE strategy_id = ?
                ORDER BY timestamp ASC
            """, (strategy_id,))

            trades = []
            cumulative_pnl = 0
            for row in cur.fetchall():
                cumulative_pnl += (row[4] or 0)
                trades.append({
                    "side": row[0],
                    "price": row[1],
                    "amount_usd": row[2],
                    "timestamp": row[3],
                    "pnl_usd": row[4],
                    "cumulative_pnl": cumulative_pnl,
                })

        # Calculate metrics
        if len(trades) == 0:
            return {"trades": [], "metrics": {}}

        total_trades = len(trades)
        profitable_trades = len([t for t in trades if t["pnl_usd"] and t["pnl_usd"] > 0])
        win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0

        return {
            "trades": trades,
            "metrics": {
                "total_trades": total_trades,
                "profitable_trades": profitable_trades,
                "win_rate": win_rate,
                "total_pnl": cumulative_pnl,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# ALERTS ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.get("/alerts")
async def get_alerts(unread_only: bool = False, limit: int = 50):
    """Get alerts"""
    try:
        if unread_only:
            alerts = db.get_unread_alerts(limit)
        else:
            with db._get_conn() as conn:
                cur = conn.cursor()
                cur.execute("""
                    SELECT id, token_address, triggered_at, message, priority, read, metadata
                    FROM alert_history
                    ORDER BY triggered_at DESC
                    LIMIT ?
                """, (limit,))

                alerts = []
                for row in cur.fetchall():
                    import json
                    alerts.append({
                        "id": row[0],
                        "token_address": row[1],
                        "triggered_at": row[2],
                        "message": row[3],
                        "priority": row[4],
                        "read": bool(row[5]),
                        "metadata": json.loads(row[6]) if row[6] else {},
                    })

        return {"alerts": alerts, "count": len(alerts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts")
async def create_alert(alert: AlertCreate):
    """Create a new alert"""
    try:
        alert_id = db.create_alert(
            alert.token_address,
            alert.message,
            alert.priority,
            metadata=alert.metadata
        )
        return {"id": alert_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/alerts/{alert_id}/read")
async def mark_alert_read(alert_id: int):
    """Mark alert as read"""
    try:
        db.mark_alert_read(alert_id)
        return {"id": alert_id, "status": "read"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# SCANNER ENDPOINTS (Helix Integration)
# ═══════════════════════════════════════════════════════════

@router.get("/scanner/signals")
async def get_scanner_signals(hours: int = 24, limit: int = 100):
    """Get recent signals from Helix scanner"""
    try:
        signals = db.get_recent_helix_signals(hours, limit)
        return {"signals": signals, "count": len(signals)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# CONFIG ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.get("/config")
async def get_all_configs():
    """Get all system configurations"""
    try:
        configs = db.get_all_configs()
        return {"configs": configs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/config")
async def update_config(update: ConfigUpdate):
    """Update a configuration value"""
    try:
        db.set_config(update.key, update.value)
        return {"key": update.key, "value": update.value, "status": "updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# HEALTH & STATS
# ═══════════════════════════════════════════════════════════

@router.get("/health")
async def aura_health():
    """AURA system health check"""
    try:
        # Check database
        with db._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM tokens")
            token_count = cur.fetchone()[0]

        # Check Helix signals
        signals = db.get_recent_helix_signals(hours=1, limit=1)
        helix_active = len(signals) > 0

        return {
            "status": "healthy",
            "aura_db": "connected",
            "tokens_tracked": token_count,
            "helix_scanner": "active" if helix_active else "idle",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_stats():
    """Get overall system statistics"""
    try:
        with db._get_conn() as conn:
            cur = conn.cursor()

            # Count various entities
            cur.execute("SELECT COUNT(*) FROM tokens")
            total_tokens = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM watchlist")
            watchlist_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM portfolio_items WHERE status = 'open'")
            open_positions = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM alert_history WHERE read = 0")
            unread_alerts = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM strategies WHERE status = 'active'")
            active_strategies = cur.fetchone()[0]

        # Get Helix signal count
        signals = db.get_recent_helix_signals(hours=24, limit=10000)

        return {
            "tokens_tracked": total_tokens,
            "watchlist_size": watchlist_count,
            "open_positions": open_positions,
            "unread_alerts": unread_alerts,
            "active_strategies": active_strategies,
            "signals_24h": len(signals),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# CHAT INTERFACE
# ═══════════════════════════════════════════════════════════

class ChatQuery(BaseModel):
    query: str

@router.post("/chat")
async def chat_query(chat: ChatQuery):
    """Natural language query interface"""
    try:
        from .chat import chat as chat_engine
        response = chat_engine.process_query(chat.query)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/suggestions")
async def chat_suggestions():
    """Get smart chat suggestions"""
    return {
        "suggestions": [
            "Show me my portfolio",
            "What's in my watchlist?",
            "Show recent signals",
            "How are my strategies performing?",
            "Give me system stats",
            "What tokens should I watch?",
        ]
    }

# ═══════════════════════════════════════════════════════════
# GOVERNANCE ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.get("/governance/proposals")
async def get_proposals():
    """Get all active governance proposals"""
    try:
        from .governance import governance
        proposals = governance.get_active_proposals()
        return {"proposals": proposals}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/governance/proposals/{proposal_id}")
async def get_proposal(proposal_id: int):
    """Get proposal details and voting results"""
    try:
        from .governance import governance
        proposal = governance.get_proposal(proposal_id)
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")

        results = governance.get_voting_results(proposal_id)

        return {
            "proposal": proposal,
            "voting_results": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/governance/proposals")
async def create_proposal(
    title: str,
    description: str,
    proposal_type: str,
    proposed_changes: Dict,
    user_id: int = 1,
):
    """Create a new governance proposal"""
    try:
        from .governance import governance
        proposal_id = governance.create_proposal(
            title, description, proposal_type, proposed_changes, user_id
        )
        return {"proposal_id": proposal_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/governance/proposals/{proposal_id}/vote")
async def vote_on_proposal(proposal_id: int, vote: str, user_id: int = 1):
    """Cast a vote on a proposal"""
    try:
        from .governance import governance
        success = governance.cast_vote(proposal_id, user_id, vote)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# SENTIMENT ANALYSIS ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.get("/sentiment/{address}")
async def get_token_sentiment(address: str):
    """Get sentiment analysis for a token"""
    try:
        from .sentiment import sentiment_analyzer
        token = db.get_token(address)
        if not token:
            raise HTTPException(status_code=404, detail="Token not found")

        sentiment = await sentiment_analyzer.analyze_token_sentiment(
            address, token["symbol"]
        )
        return sentiment
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sentiment/trending")
async def get_trending_tokens():
    """Get tokens trending on social media"""
    try:
        from .sentiment import sentiment_analyzer
        trending = await sentiment_analyzer.get_trending_tokens()
        return {"trending": trending}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# WHALE TRACKING ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.get("/whales/signals")
async def get_whale_signals():
    """Get current whale copy trading signals"""
    try:
        from .whale_tracker import whale_tracker
        signals = await whale_tracker.get_whale_copy_signals()
        return {"signals": signals}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/whales/{whale_address}/activity")
async def get_whale_activity(whale_address: str):
    """Get recent trading activity for a whale wallet"""
    try:
        from .whale_tracker import whale_tracker
        activity = await whale_tracker.track_whale_activity(whale_address)
        return {"whale_address": whale_address, "activity": activity}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/whales/{address}/is-buying")
async def check_whale_buying(address: str):
    """Check if whales are buying a specific token"""
    try:
        from .whale_tracker import whale_tracker
        is_buying = whale_tracker.is_whale_buying(address)
        return {"token_address": address, "whales_buying": is_buying}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# ANALYTICS ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.post("/analytics/backtest/{strategy_id}")
async def backtest_strategy(
    strategy_id: int,
    start_date: str,
    end_date: str,
    initial_capital: float = 10000,
):
    """Backtest a strategy on historical data"""
    try:
        from .analytics import analytics
        from datetime import datetime

        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)

        results = analytics.backtest_strategy(strategy_id, start, end, initial_capital)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analytics/monte-carlo/{strategy_id}")
async def monte_carlo_simulation(
    strategy_id: int, num_simulations: int = 1000, initial_capital: float = 10000
):
    """Run Monte Carlo simulation on strategy"""
    try:
        from .analytics import analytics

        results = analytics.monte_carlo_simulation(
            strategy_id, num_simulations, initial_capital
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/metrics/{strategy_id}")
async def get_strategy_metrics(strategy_id: int):
    """Get risk-adjusted metrics for a strategy"""
    try:
        from .analytics import analytics

        sharpe = analytics.calculate_sharpe_ratio(strategy_id)
        sortino = analytics.calculate_sortino_ratio(strategy_id)
        max_dd = analytics.calculate_max_drawdown(strategy_id)

        return {
            "strategy_id": strategy_id,
            "sharpe_ratio": sharpe,
            "sortino_ratio": sortino,
            "max_drawdown": max_dd,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
