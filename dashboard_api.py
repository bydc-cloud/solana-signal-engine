"""
AURA Dashboard API
FastAPI routes for the trading dashboard
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import asyncio

from aura.database import db
from aura.mcp_toolkit import mcp_toolkit, MCP_TOOLKIT_AVAILABLE

router = APIRouter(prefix="/api", tags=["dashboard"])


# ═══════════════════════════════════════════════════════════
# DATA MODELS (Pydantic)
# ═══════════════════════════════════════════════════════════

class PortfolioResponse(BaseModel):
    """Portfolio summary response"""
    open_positions: int
    closed_positions: int
    open_value_usd: float
    total_pnl_usd: float
    total_pnl_percent: float
    win_rate: float
    best_performer: Optional[Dict]
    worst_performer: Optional[Dict]
    positions: List[Dict]


class WatchlistResponse(BaseModel):
    """Watchlist response"""
    count: int
    tokens: List[Dict]


class TokenDetailResponse(BaseModel):
    """Token detail response"""
    address: str
    symbol: str
    name: str
    price: float
    market_cap: float
    liquidity: float
    volume_24h: float
    price_change_24h: float
    logo_uri: Optional[str]
    coingecko_rank: Optional[int]
    facts: List[Dict]
    ohlc: List[Dict]
    tvl: List[Dict]


class TradesResponse(BaseModel):
    """Trades response"""
    total: int
    active: int
    closed: int
    trades: List[Dict]


class StrategiesResponse(BaseModel):
    """Strategies response"""
    total: int
    active: int
    strategies: List[Dict]


class AlertsResponse(BaseModel):
    """Alerts response"""
    total: int
    unread: int
    alerts: List[Dict]


class ShareTelegramRequest(BaseModel):
    """Share to Telegram request"""
    title: str
    message: str
    image_url: Optional[str] = None


# ═══════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.get("/portfolio", response_model=PortfolioResponse)
async def get_portfolio():
    """
    GET /api/portfolio
    Returns portfolio summary with open/closed positions and P&L
    """
    try:
        summary = db.get_portfolio_summary()
        positions = db.get_open_positions()

        # Find best/worst performers
        if positions:
            best = max(positions, key=lambda p: p.get("pnl_percent", 0))
            worst = min(positions, key=lambda p: p.get("pnl_percent", 0))
        else:
            best = None
            worst = None

        return PortfolioResponse(
            open_positions=summary["open_positions"],
            closed_positions=summary["closed_positions"],
            open_value_usd=summary["open_value_usd"],
            total_pnl_usd=summary["total_pnl_usd"],
            total_pnl_percent=summary.get("avg_pnl_percent", 0),  # Use avg_pnl_percent from DB
            win_rate=summary["win_rate"],
            best_performer=best,
            worst_performer=worst,
            positions=positions
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Portfolio error: {str(e)}")


@router.get("/watchlist", response_model=WatchlistResponse)
async def get_watchlist():
    """
    GET /api/watchlist
    Returns watchlist tokens
    """
    try:
        watchlist = db.get_watchlist()

        # Enrich with current prices if MCP available
        if MCP_TOOLKIT_AVAILABLE:
            for item in watchlist:
                try:
                    symbol = item.get("symbol", "")
                    price = await mcp_toolkit.get_token_price(symbol.lower())
                    item["current_price"] = price
                except:
                    item["current_price"] = 0

        return WatchlistResponse(
            count=len(watchlist),
            tokens=watchlist
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Watchlist error: {e}")


@router.get("/token/{address}", response_model=TokenDetailResponse)
async def get_token_detail(address: str):
    """
    GET /api/token/:address
    Returns detailed token information including OHLC, TVL, facts
    """
    try:
        # Get token from database
        with db._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM tokens WHERE address = ?", (address,))
            row = cur.fetchone()

            if not row:
                raise HTTPException(status_code=404, detail="Token not found")

            import json
            metadata = json.loads(row[5]) if row[5] else {}

            # Get facts
            cur.execute("""
                SELECT fact_type, fact, source, confidence, created_at
                FROM token_facts
                WHERE token_address = ?
                ORDER BY created_at DESC
                LIMIT 50
            """, (address,))

            facts = [
                {
                    "type": r[0],
                    "fact": r[1],
                    "source": r[2],
                    "confidence": r[3],
                    "created_at": r[4]
                }
                for r in cur.fetchall()
            ]

            # Get OHLC data (last 24h, 1h timeframe)
            cur.execute("""
                SELECT timestamp, open, high, low, close, volume_usd
                FROM token_price_ohlc
                WHERE token_address = ? AND timeframe = '1h'
                ORDER BY timestamp DESC
                LIMIT 24
            """, (address,))

            ohlc = [
                {
                    "timestamp": r[0],
                    "open": r[1],
                    "high": r[2],
                    "low": r[3],
                    "close": r[4],
                    "volume": r[5]
                }
                for r in cur.fetchall()
            ]

            # Get TVL data
            cur.execute("""
                SELECT timestamp, tvl_usd, liquidity_usd, source
                FROM token_tvl
                WHERE token_address = ?
                ORDER BY timestamp DESC
                LIMIT 100
            """, (address,))

            tvl = [
                {
                    "timestamp": r[0],
                    "tvl": r[1],
                    "liquidity": r[2],
                    "source": r[3]
                }
                for r in cur.fetchall()
            ]

        # Enrich with CoinGecko data if available
        if MCP_TOOLKIT_AVAILABLE:
            try:
                market_data = await mcp_toolkit.get_token_market_data(row[2])  # symbol
                if market_data:
                    metadata.update(market_data)
            except:
                pass

        return TokenDetailResponse(
            address=row[1],
            symbol=row[2],
            name=row[3],
            price=metadata.get("price", 0),
            market_cap=metadata.get("mc", 0),
            liquidity=metadata.get("liquidity", 0),
            volume_24h=metadata.get("volume_24h", 0),
            price_change_24h=metadata.get("price_change_24h", 0),
            logo_uri=row[4],
            coingecko_rank=metadata.get("coingecko_rank"),
            facts=facts,
            ohlc=ohlc,
            tvl=tvl
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token detail error: {e}")


@router.get("/trades", response_model=TradesResponse)
async def get_trades(status: Optional[str] = Query(None, regex="^(active|closed)$")):
    """
    GET /api/trades?status=active|closed
    Returns trades filtered by status
    """
    try:
        with db._get_conn() as conn:
            cur = conn.cursor()

            if status:
                cur.execute("""
                    SELECT id, token_address, symbol, side, price, amount, value_usd,
                           status, entry_price, exit_price, pnl_usd, pnl_percent,
                           strategy_id, notes, opened_at, closed_at
                    FROM trades
                    WHERE status = ?
                    ORDER BY opened_at DESC
                    LIMIT 100
                """, (status,))
            else:
                cur.execute("""
                    SELECT id, token_address, symbol, side, price, amount, value_usd,
                           status, entry_price, exit_price, pnl_usd, pnl_percent,
                           strategy_id, notes, opened_at, closed_at
                    FROM trades
                    ORDER BY opened_at DESC
                    LIMIT 100
                """)

            trades = [
                {
                    "id": r[0],
                    "token_address": r[1],
                    "symbol": r[2],
                    "side": r[3],
                    "price": r[4],
                    "amount": r[5],
                    "value_usd": r[6],
                    "status": r[7],
                    "entry_price": r[8],
                    "exit_price": r[9],
                    "pnl_usd": r[10],
                    "pnl_percent": r[11],
                    "strategy_id": r[12],
                    "notes": r[13],
                    "opened_at": r[14],
                    "closed_at": r[15]
                }
                for r in cur.fetchall()
            ]

            active_count = sum(1 for t in trades if t["status"] == "active")
            closed_count = sum(1 for t in trades if t["status"] == "closed")

        return TradesResponse(
            total=len(trades),
            active=active_count,
            closed=closed_count,
            trades=trades
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trades error: {e}")


@router.get("/strategies", response_model=StrategiesResponse)
async def get_strategies():
    """
    GET /api/strategies
    Returns all strategies with stats
    """
    try:
        strategies = db.get_active_strategies()
        active_count = sum(1 for s in strategies if s.get("enabled", 0) == 1)

        return StrategiesResponse(
            total=len(strategies),
            active=active_count,
            strategies=strategies
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Strategies error: {e}")


@router.get("/alerts", response_model=AlertsResponse)
async def get_alerts(limit: int = Query(50, ge=1, le=500)):
    """
    GET /api/alerts?limit=50
    Returns recent alerts
    """
    try:
        with db._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, token_address, title, message, priority, status,
                       alert_config_id, metadata_json, created_at, read_at
                FROM alerts
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))

            alerts = [
                {
                    "id": r[0],
                    "token_address": r[1],
                    "title": r[2],
                    "message": r[3],
                    "priority": r[4],
                    "status": r[5],
                    "alert_config_id": r[6],
                    "metadata": r[7],
                    "created_at": r[8],
                    "read_at": r[9]
                }
                for r in cur.fetchall()
            ]

            unread_count = sum(1 for a in alerts if a["status"] == "unread")

        return AlertsResponse(
            total=len(alerts),
            unread=unread_count,
            alerts=alerts
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Alerts error: {e}")


@router.post("/actions/shareTelegram")
async def share_to_telegram(request: ShareTelegramRequest):
    """
    POST /api/actions/shareTelegram
    Shares content to Telegram
    """
    try:
        from aura.telegram_bot import telegram_bot

        if not telegram_bot.enabled:
            raise HTTPException(status_code=503, detail="Telegram bot not configured")

        # Format message
        message = f"*{request.title}*\n\n{request.message}"

        if request.image_url:
            message += f"\n\n[View Chart]({request.image_url})"

        # Send via Telegram MCP
        success = await telegram_bot.send_message(message)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to send Telegram message")

        return {"success": True, "message": "Shared to Telegram"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Telegram error: {e}")


@router.post("/actions/refresh")
async def trigger_refresh():
    """
    POST /api/actions/refresh
    Triggers a manual refresh of scanner/worker
    """
    try:
        # Trigger autonomous engine to process signals
        from aura.autonomous import autonomous_engine

        processed = autonomous_engine.process_new_signals()

        return {
            "success": True,
            "message": f"Refresh triggered, processed {processed} signals"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refresh error: {e}")


# ═══════════════════════════════════════════════════════════
# SQL QUERIES EXAMPLES (for reference)
# ═══════════════════════════════════════════════════════════
"""
Portfolio Summary:
    SELECT
        COUNT(CASE WHEN status = 'active' THEN 1 END) as open_positions,
        COUNT(CASE WHEN status = 'closed' THEN 1 END) as closed_positions,
        SUM(CASE WHEN status = 'active' THEN value_usd ELSE 0 END) as open_value_usd,
        SUM(pnl_usd) as total_pnl_usd,
        AVG(pnl_percent) as avg_pnl_percent,
        SUM(CASE WHEN pnl_usd > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as win_rate
    FROM trades;

Top Movers (24h):
    SELECT t.symbol, t.address,
           (o2.close - o1.close) / o1.close * 100 as price_change_percent,
           o2.volume_usd as volume_24h
    FROM tokens t
    JOIN token_price_ohlc o1 ON t.address = o1.token_address AND o1.timestamp = ?  -- 24h ago
    JOIN token_price_ohlc o2 ON t.address = o2.token_address AND o2.timestamp = ?  -- now
    WHERE o1.timeframe = '1d' AND o2.timeframe = '1d'
    ORDER BY price_change_percent DESC
    LIMIT 10;

Recent Signals:
    SELECT s.symbol, s.momentum_score, s.payload_json, s.created_at
    FROM helix_signals s
    WHERE s.created_at >= datetime('now', '-24 hours')
    ORDER BY s.momentum_score DESC
    LIMIT 20;
"""
