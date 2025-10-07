#!/usr/bin/env python3
"""
AURA Unified API Server
Combines Helix scanner APIs with AURA autonomous intelligence system
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import asyncio
import logging

logger = logging.getLogger(__name__)

# Import Helix existing endpoints (they're standalone functions, not a router)
from api_server import get_status, get_alerts, get_logs

# Import AURA routes
from aura.api import router as aura_router
from aura.websocket_manager import websocket_manager

# Import Dashboard API routes
from dashboard_api import router as dashboard_router

# Create unified app
app = FastAPI(
    title="AURA - Autonomous Crypto Intelligence",
    description="Unified API combining Helix scanner with AURA autonomous agent",
    version="0.2.1"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Helix routes (existing scanner APIs)
# Keep existing paths for backward compatibility
@app.get("/status")
async def status():
    """Helix scanner status (legacy endpoint)"""
    return await get_status()

@app.get("/alerts")
async def alerts(hours: int = 24, limit: int = 100):
    """Helix scanner alerts (legacy endpoint)"""
    return await get_alerts(hours, limit)

@app.get("/logs")
async def logs(limit: int = 100):
    """Helix scanner logs (legacy endpoint)"""
    return await get_logs(limit)

# Mount AURA routes under /api prefix
app.include_router(aura_router, prefix="/api/aura", tags=["AURA"])

# Mount Dashboard API routes under /api prefix
app.include_router(dashboard_router, tags=["Dashboard"])

# Unified health check
@app.get("/health")
async def health():
    """Combined system health"""
    from aura.database import db

    # Check Helix
    helix_status = await get_status()

    # Check AURA
    try:
        with db._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM tokens")
            token_count = cur.fetchone()[0]
        aura_status = "healthy"
    except Exception as e:
        aura_status = f"error: {e}"
        token_count = 0

    return {
        "status": "healthy" if aura_status == "healthy" else "degraded",
        "helix": {
            "scanner_running": helix_status.get("scanner_running"),
            "database_initialized": helix_status.get("database_initialized"),
        },
        "aura": {
            "status": aura_status,
            "tokens_tracked": token_count,
        },
        "timestamp": helix_status.get("timestamp"),
    }

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time dashboard updates
    Clients receive:
    - New signals
    - Portfolio updates
    - Watchlist changes
    - Strategy executions
    - System alerts
    """
    await websocket.accept()
    await websocket_manager.connect(websocket)

    try:
        while True:
            # Keep connection alive and listen for client messages
            data = await websocket.receive_text()
            # Echo back for testing
            await websocket.send_text(f"Echo: {data}")

    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket_manager.disconnect(websocket)

# Mount Lovable dashboard static files
app.mount("/assets", StaticFiles(directory="lovable_dashboard/dist/assets"), name="assets")

# Dashboard endpoint - AURA Live Dashboard (default, cyber theme with AURA API)
@app.get("/dashboard")
async def dashboard():
    """Serve the AURA Live Dashboard with real-time data and cyber aesthetic"""
    return FileResponse("dashboard/aura-live.html")

# Firecrawl-style dashboard (alternative)
@app.get("/dashboard/firecrawl")
async def dashboard_firecrawl():
    """Serve the Firecrawl-style dashboard"""
    return FileResponse("dashboard/firecrawl-style.html")

# Lovable dashboard (Supabase-based, for reference)
@app.get("/dashboard/lovable")
async def dashboard_lovable():
    """Serve the Lovable React dashboard (uses Supabase backend)"""
    return FileResponse("lovable_dashboard/dist/index.html")

# Simple dashboard (legacy)
@app.get("/dashboard/simple")
async def dashboard_simple():
    """Serve the simple dashboard"""
    return FileResponse("dashboard/index.html")

# Mount static files for dashboard assets (if any)
# app.mount("/dashboard/static", StaticFiles(directory="dashboard/static"), name="dashboard-static")

# Telegram Webhook Handler with Full AI Support
@app.post("/telegram/webhook")
async def telegram_webhook(update: dict):
    """Handle incoming Telegram messages via webhook with full AI capabilities"""
    try:
        import os
        import aiohttp
        from aura.database import db
        from datetime import datetime

        message = update.get('message', {})
        if not message:
            return {"ok": True}

        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '')
        user_id = message.get('from', {}).get('id', 0)
        username = message.get('from', {}).get('username') or message.get('from', {}).get('first_name', 'User')

        if not text or not chat_id:
            return {"ok": True}

        logger.info(f"📱 Telegram message from {username} ({chat_id}): {text}")

        # Get system context
        portfolio = db.get_portfolio_summary()
        watchlist = db.get_watchlist()
        signals = db.get_recent_helix_signals(hours=24, limit=5)

        # Store conversation in memory
        try:
            timestamp = datetime.now().isoformat()
            with db._get_conn() as conn:
                cur = conn.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS conversation_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        username TEXT,
                        message TEXT,
                        message_type TEXT,
                        portfolio_summary TEXT,
                        signals_count INTEGER,
                        watchlist_count INTEGER,
                        timestamp TEXT
                    )
                """)
                cur.execute("""
                    INSERT INTO conversation_log (user_id, username, message, message_type, portfolio_summary, signals_count, watchlist_count, timestamp)
                    VALUES (?, ?, ?, 'user', ?, ?, ?, ?)
                """, (
                    user_id, username, text,
                    f"{portfolio['open_positions']} positions, ${portfolio['total_pnl_usd']:.2f} P&L",
                    len(signals), len(watchlist), timestamp
                ))
                conn.commit()
        except Exception as e:
            logger.warning(f"Memory storage error: {e}")

        # Generate intelligent response
        response_text = ""
        text_lower = text.lower()

        if text.startswith('/start'):
            response_text = "*AURA v0.3.0 - Autonomous Intelligence*\n\n"
            response_text += "*Trading:*\n"
            response_text += "/portfolio - Portfolio summary\n"
            response_text += "/signals - Recent signals\n"
            response_text += "/watchlist - Tracked tokens\n\n"
            response_text += "*Autonomous Control:*\n"
            response_text += "/status - Project status\n"
            response_text += "/deploy - Deploy to Railway\n"
            response_text += "/changes - Recent changes\n"
            response_text += "/analyze - Codebase analysis\n\n"
            response_text += "Or just talk naturally - I understand context!"

        elif text.startswith('/portfolio'):
            response_text = f"💼 *Portfolio Summary*\n\n"
            response_text += f"• Open Positions: {portfolio['open_positions']}\n"
            response_text += f"• Portfolio Value: ${portfolio['open_value_usd']:,.2f}\n"
            response_text += f"• Total P&L: ${portfolio['total_pnl_usd']:,.2f} ({portfolio['total_pnl_percent']:+.2f}%)\n"
            response_text += f"• Win Rate: {portfolio['win_rate']:.1f}%"

        elif text.startswith('/signals'):
            response_text = f"📡 *Recent Signals* (last 24h)\n\n"
            if signals:
                for sig in signals[:5]:
                    symbol = sig.get('symbol', 'Unknown')
                    momentum = sig.get('momentum_score', 0)
                    address = sig.get('token_address', '')
                    response_text += f"• [{symbol}](https://dexscreener.com/solana/{address}) - Momentum: {momentum:.1f}\n"
                response_text += f"\n{len(signals)} total signals"
            else:
                response_text += "No signals in last 24h"

        elif text.startswith('/watchlist'):
            response_text = f"*Watchlist* ({len(watchlist)} tokens)\n\n"
            if watchlist:
                for item in watchlist[:5]:
                    symbol = item.get('symbol', 'Unknown')
                    address = item.get('token_address', '')
                    response_text += f"• [{symbol}](https://dexscreener.com/solana/{address})\n"
                response_text += f"\nClick tokens to view on Dexscreener"
            else:
                response_text += "Watchlist is empty"

        # AUTONOMOUS CONTROL COMMANDS
        elif text.startswith('/status'):
            from aura.autonomous_controller import autonomous_controller
            summary = await autonomous_controller.get_project_summary()
            response_text = "*Project Status*\n\n"
            response_text += f"📁 Python Files: {summary.get('python_files', 'N/A')}\n"
            response_text += f"📍 Root: `{summary.get('project_root', 'N/A')}`\n\n"
            git_status = summary.get('git_status', '').strip()
            if git_status:
                response_text += f"*Git Status:*\n```\n{git_status[:200]}\n```"
            else:
                response_text += "*Git Status:* Clean working tree"

        elif text.startswith('/deploy'):
            from aura.autonomous_controller import autonomous_controller
            response_text = "*Deploying to Railway...*\n\n"
            response_text += "This will:\n"
            response_text += "1. Push code to GitHub\n"
            response_text += "2. Trigger Railway build\n"
            response_text += "3. Deploy new version\n\n"
            response_text += "⏳ Starting deployment..."

            # Send initial message
            bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
            if bot_token:
                async with aiohttp.ClientSession() as session:
                    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                    await session.post(url, json={
                        "chat_id": chat_id,
                        "text": response_text,
                        "parse_mode": "Markdown"
                    })

            # Actually deploy
            result = await autonomous_controller.deploy_to_railway()
            if result.get('success'):
                response_text = "✅ *Deployment Successful!*\n\n"
                response_text += "Check Railway dashboard for build logs."
            else:
                response_text = f"❌ *Deployment Failed*\n\n"
                response_text += f"Error: {result.get('error', 'Unknown error')}"

        elif text.startswith('/changes'):
            from aura.autonomous_controller import autonomous_controller
            changes = await autonomous_controller.get_recent_changes(days=7)
            response_text = "*Recent Changes (7 days)*\n\n"
            if changes and len(changes) > 10:
                response_text += f"```\n{changes[:1500]}\n```\n\n"
                response_text += "Use `/changes 1` for last day"
            else:
                response_text += "No recent changes"

        elif text.startswith('/analyze'):
            from aura.autonomous_controller import autonomous_controller
            query = text.replace('/analyze', '').strip()
            if not query:
                response_text = "*Codebase Analysis*\n\n"
                response_text += "Ask me:\n"
                response_text += "• /analyze files\n"
                response_text += "• /analyze database\n"
                response_text += "• /analyze api\n"
                response_text += "• /analyze dependencies"
            else:
                analysis = await autonomous_controller.analyze_codebase(query)
                response_text = f"*Analysis: {query}*\n\n"
                response_text += f"```\n{analysis[:1500]}\n```"

        elif "portfolio" in text_lower or "pnl" in text_lower or "position" in text_lower:
            response_text = f"💼 Current Portfolio:\n\n"
            response_text += f"• Open Positions: {portfolio['open_positions']}\n"
            response_text += f"• Total P&L: ${portfolio['total_pnl_usd']:,.2f}\n"
            response_text += f"• Win Rate: {portfolio['win_rate']:.1f}%\n\n"
            response_text += "Use /portfolio for full details"

        elif "signal" in text_lower:
            response_text = f"📡 Recent Signals: {len(signals)} in last 24h\n\n"
            if signals:
                for sig in signals[:3]:
                    symbol = sig.get('symbol', 'Unknown')
                    momentum = sig.get('momentum_score', 0)
                    response_text += f"• {symbol}: {momentum:.1f}\n"
                response_text += "\nUse /signals for more"
            else:
                response_text += "No recent signals"

        elif "watch" in text_lower:
            response_text = f"👀 Watchlist: {len(watchlist)} tokens\n\n"
            if watchlist:
                for item in watchlist[:3]:
                    response_text += f"• {item.get('symbol', 'Unknown')}\n"
                response_text += "\nUse /watchlist for full list"
            else:
                response_text += "Watchlist is empty"

        elif "price" in text_lower or "chart" in text_lower or "token" in text_lower:
            # Try to extract token symbol/address from message
            words = text.split()
            potential_symbol = None
            for word in words:
                if word.isupper() and len(word) <= 10:  # Likely a token symbol
                    potential_symbol = word
                    break

            if potential_symbol:
                # Look up token in watchlist or signals
                token_info = None
                for item in watchlist:
                    if item.get('symbol', '').upper() == potential_symbol:
                        token_info = item
                        break

                if not token_info and signals:
                    for sig in signals:
                        if sig.get('symbol', '').upper() == potential_symbol:
                            token_info = sig
                            break

                if token_info:
                    address = token_info.get('token_address', '')
                    symbol = token_info.get('symbol', potential_symbol)
                    response_text = f"📊 *{symbol}* Token Info\n\n"

                    if 'price_usd' in token_info:
                        response_text += f"💰 Price: ${token_info['price_usd']:.8f}\n"
                    if 'market_cap' in token_info:
                        response_text += f"📈 Market Cap: ${token_info['market_cap']:,.0f}\n"
                    if 'volume_24h' in token_info:
                        response_text += f"💹 24h Volume: ${token_info['volume_24h']:,.0f}\n"
                    if 'momentum_score' in token_info:
                        response_text += f"🚀 Momentum: {token_info['momentum_score']:.1f}\n"

                    response_text += f"\n[View on Dexscreener](https://dexscreener.com/solana/{address})"
                else:
                    response_text = f"🔍 Token {potential_symbol} not found in watchlist or recent signals.\n\n"
                    response_text += "Add tokens to watchlist to track them!"
            else:
                response_text = "🔍 Please specify a token symbol (e.g., 'show me SOL price')"

        else:
            response_text = f"🤖 *AURA Intelligence*\n\n"
            response_text += f"I understand you're asking: _{text}_\n\n"
            response_text += f"Current Status:\n"
            response_text += f"💼 Portfolio: {portfolio['open_positions']} positions, ${portfolio['total_pnl_usd']:,.2f} P&L\n"
            response_text += f"📡 Signals: {len(signals)} in last 24h\n"
            response_text += f"👀 Watchlist: {len(watchlist)} tokens\n\n"
            response_text += "Ask me about portfolio, signals, watchlist, or token prices!"

        # Store bot response
        try:
            with db._get_conn() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO conversation_log (user_id, username, message, message_type, timestamp)
                    VALUES (?, ?, ?, 'bot', ?)
                """, (user_id, username, response_text, datetime.now().isoformat()))
                conn.commit()
        except Exception as e:
            logger.warning(f"Response memory storage error: {e}")

        # Send response
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if bot_token and response_text:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                await session.post(url, json={
                    "chat_id": chat_id,
                    "text": response_text,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": True
                })

        return {"ok": True}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"ok": False}

# Root endpoint
@app.get("/")
async def root():
    """API information"""
    return {
        "name": "AURA - Autonomous Crypto Intelligence",
        "version": "0.3.0",
        "endpoints": {
            "helix_legacy": ["/status", "/alerts", "/logs"],
            "aura": ["/api/portfolio", "/api/watchlist", "/api/tokens", "/api/strategies", "/api/alerts", "/api/config"],
            "health": ["/health"],
            "websocket": ["/ws"],
            "dashboard": ["/dashboard"],
        },
        "docs": "/docs",
    }

# Start heartbeat task on startup
@app.on_event("startup")
async def startup_event():
    """Start background tasks"""
    asyncio.create_task(websocket_manager.heartbeat())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
