#!/usr/bin/env python3
"""
AURA Unified API Server
Combines Helix scanner APIs with AURA autonomous intelligence system
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import logging

logger = logging.getLogger(__name__)

# Import Helix existing endpoints (they're standalone functions, not a router)
from api_server import get_status, get_alerts, get_logs

# Import AURA routes
from aura.api import router as aura_router
from aura.websocket_manager import websocket_manager

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
app.include_router(aura_router, prefix="/api", tags=["AURA"])

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

# Root endpoint
@app.get("/")
async def root():
    """API information"""
    return {
        "name": "AURA - Autonomous Crypto Intelligence",
        "version": "0.2.1",
        "endpoints": {
            "helix_legacy": ["/status", "/alerts", "/logs"],
            "aura": ["/api/portfolio", "/api/watchlist", "/api/tokens", "/api/strategies", "/api/alerts", "/api/config"],
            "health": ["/health"],
            "websocket": ["/ws"],
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
