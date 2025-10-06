#!/usr/bin/env python3
"""
AURA Unified API Server
Combines Helix scanner APIs with AURA autonomous intelligence system
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import Helix existing routes
from api_server import (
    get_status,
    get_alerts,
    get_logs,
    router as helix_router
)

# Import AURA routes
from aura.api import router as aura_router

# Create unified app
app = FastAPI(
    title="AURA - Autonomous Crypto Intelligence",
    description="Unified API combining Helix scanner with AURA autonomous agent",
    version="0.1.0"
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

# Root endpoint
@app.get("/")
async def root():
    """API information"""
    return {
        "name": "AURA - Autonomous Crypto Intelligence",
        "version": "0.1.0",
        "endpoints": {
            "helix_legacy": ["/status", "/alerts", "/logs"],
            "aura": ["/api/portfolio", "/api/watchlist", "/api/tokens", "/api/strategies", "/api/alerts", "/api/config"],
            "health": ["/health"],
        },
        "docs": "/docs",
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
