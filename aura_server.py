#!/usr/bin/env python3
"""
AURA Unified API Server
Combines Helix scanner APIs with AURA autonomous intelligence system
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import asyncio
import logging
import os
from datetime import datetime

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

# Dashboard endpoint - AURA Control Center (default, REAL DATA)
@app.get("/")
@app.get("/dashboard")
async def dashboard():
    """Serve the AURA Control Center with real-time data - Portfolio, Signals, Watchlist"""
    return FileResponse("dashboard/aura-complete.html")

# Chat interface
@app.get("/chat")
async def dashboard_chat():
    """Serve the AURA Chat interface with AI voice"""
    return FileResponse("dashboard/aura-chat.html")

# Data dashboard (alternative, cyber theme)
@app.get("/dashboard/live")
async def dashboard_live():
    """Serve the AURA Live Dashboard with real-time trading data"""
    return FileResponse("dashboard/aura-live.html")

# Jarvis voice interface (full-screen)
@app.get("/dashboard/jarvis")
@app.get("/dashboard/aura-jarvis.html")
@app.get("/jarvis")
async def dashboard_jarvis():
    """Serve the full-screen Jarvis-style voice interface"""
    return FileResponse("dashboard/aura-jarvis-v2.html")  # Using v2 with browser speech + ElevenLabs

# Jarvis v1 (OpenAI Whisper - requires credits)
@app.get("/jarvis/v1")
async def dashboard_jarvis_v1():
    """Serve Jarvis v1 (OpenAI Whisper)"""
    return FileResponse("dashboard/aura-jarvis.html")

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

# Chat API endpoint for AURA AI interface
# Voice transcription endpoint
@app.post("/api/aura/voice")
async def aura_voice(request: Request):
    """Handle voice transcription from dashboard"""
    import tempfile
    import os as os_module

    try:
        from openai import OpenAI

        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            logger.error("OpenAI API key not configured")
            return {"error": "Voice transcription not available - API key missing", "transcription": None}

        logger.info(f"OpenAI key found: {openai_key[:8]}...")

        # Get audio file from request
        form = await request.form()
        audio_file = form.get("audio")

        if not audio_file:
            logger.error("No audio file in request")
            return {"error": "No audio file provided", "transcription": None}

        # Read audio content
        content = await audio_file.read()
        file_size = len(content)

        logger.info(f"Received audio file: {file_size} bytes, type: {audio_file.content_type}, filename: {audio_file.filename}")

        if file_size < 10:
            logger.error(f"Audio file too small: {file_size} bytes")
            return {"error": f"Audio file is too small or empty ({file_size} bytes)", "transcription": None}

        if file_size > 25000000:  # 25MB limit
            logger.error(f"Audio file too large: {file_size} bytes")
            return {"error": "Audio file is too large (max 25MB)", "transcription": None}

        # Determine file extension based on content type
        content_type = audio_file.content_type or ""
        if "webm" in content_type:
            ext = ".webm"
        elif "mp4" in content_type or "m4a" in content_type:
            ext = ".m4a"
        elif "wav" in content_type:
            ext = ".wav"
        elif "mpeg" in content_type or "mp3" in content_type:
            ext = ".mp3"
        else:
            ext = ".webm"  # Default

        logger.info(f"Using file extension: {ext}")

        # Save temporarily
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            # Transcribe with Whisper
            logger.info(f"Creating OpenAI client with key: {openai_key[:12]}...")
            client = OpenAI(api_key=openai_key)
            logger.info(f"Client created successfully")
            logger.info(f"Sending to Whisper: {tmp_path} ({os.path.getsize(tmp_path)} bytes)")

            with open(tmp_path, 'rb') as audio:
                logger.info("Calling Whisper API...")
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio,
                    language="en"  # Specify English for better accuracy
                )
                logger.info(f"Whisper success: {transcript.text[:50]}...")

            # Clean up
            os.unlink(tmp_path)

            return {
                "transcription": transcript.text,
                "timestamp": datetime.now().isoformat()
            }
        finally:
            # Ensure cleanup even on error
            if os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except:
                    pass

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Voice API error: {e}")
        logger.error(f"Full trace: {error_trace}")
        return {
            "error": f"Could not transcribe audio: {str(e)[:200]}",
            "transcription": None,
            "details": str(e)
        }

# ElevenLabs Text-to-Speech endpoint
@app.post("/api/aura/voice/elevenlabs")
async def elevenlabs_tts(request: Request):
    """Generate speech with ElevenLabs (ultra-realistic voice)"""
    try:
        data = await request.json()
        text = data.get("text", "")

        if not text:
            return {"error": "No text provided"}

        elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
        if not elevenlabs_key:
            logger.error("ElevenLabs API key not configured")
            return {"error": "ElevenLabs not configured"}

        # Call ElevenLabs API
        import aiohttp
        voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice (clear, professional)

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": elevenlabs_key,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    audio_bytes = await response.read()
                    return Response(content=audio_bytes, media_type="audio/mpeg")
                else:
                    error_text = await response.text()
                    logger.error(f"ElevenLabs error: {response.status} - {error_text}")
                    return {"error": f"ElevenLabs API error: {response.status}"}

    except Exception as e:
        logger.error(f"ElevenLabs TTS error: {e}")
        return {"error": str(e)}

# Debug endpoint to check OpenAI key
@app.get("/api/aura/debug/openai")
async def debug_openai():
    """Check if OpenAI key is configured"""
    openai_key = os.getenv("OPENAI_API_KEY")
    return {
        "openai_key_set": openai_key is not None,
        "key_length": len(openai_key) if openai_key else 0,
        "key_prefix": openai_key[:15] if openai_key else "NOT_SET"
    }

# AURA Live System Endpoints
@app.get("/api/aura/live/status")
async def get_live_status():
    """Get AURA live system status"""
    try:
        from aura.live_system import get_live_system

        system = await get_live_system()
        status = await system.get_system_status()

        return {"success": True, "status": status}
    except Exception as e:
        logger.error(f"Live status error: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/aura/live/analyze/{token_address}")
async def analyze_token_live(token_address: str):
    """Perform live analysis on a token"""
    try:
        from aura.live_system import get_live_system

        system = await get_live_system()
        analysis = await system.analyze_token_live(token_address)

        return {"success": True, "analysis": analysis}
    except Exception as e:
        logger.error(f"Live analysis error: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/aura/live/config")
async def get_live_config():
    """Get live system configuration"""
    try:
        from aura_live_config import AuraLiveConfig

        config = AuraLiveConfig()
        summary = config.get_configuration_summary()

        return {"success": True, "config": summary}
    except Exception as e:
        logger.error(f"Live config error: {e}")
        return {"success": False, "error": str(e)}

# Railway initialization endpoint
@app.post("/api/aura/init")
async def initialize_railway():
    """Initialize Railway database with seed data"""
    try:
        import sqlite3
        logger.info("Starting Railway initialization...")

        conn = sqlite3.connect('aura.db')
        cur = conn.cursor()

        # Seed whale wallets
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tracked_wallets (
                address TEXT PRIMARY KEY,
                win_rate REAL DEFAULT 0,
                avg_pnl REAL DEFAULT 0,
                total_trades INTEGER DEFAULT 0,
                successful_trades INTEGER DEFAULT 0,
                total_pnl REAL DEFAULT 0,
                first_seen TEXT,
                last_updated TEXT,
                is_active INTEGER DEFAULT 1,
                tokens_traded TEXT
            )
        """)

        whales = [
            ('7YttLkHDoNj9wyDur5pM1ejNaAvT9X4eqaYcHQqtj2G5', 68.5, 3654.75, 127, 87, 456789.50, 'BONK,WIF,MYRO,JUP,PYTH'),
            ('DYw8jCTfwHNRJhhmFcbXvVDTqWMEVFBX6ZKUmG5CNSKK', 72.1, 3511.18, 89, 64, 312456.25, 'SOL,BONK,JTO,RNDR,RAY'),
            ('5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1', 61.2, 808.51, 234, 143, 189234.75, 'SAMO,COPE,FIDA,KIN,SRM'),
            ('3vEHvV5FLRPKhLGvPfpxqvRN6jR6HCzWWPgxKqfJjZXh', 78.6, 4188.34, 56, 44, 234567.00, 'JUP,PYTH,MNGO,ORCA,STEP'),
            ('8BnEgHoWFysVcuFFX7QztDmzuH8r5ZFvyP3sYwn1XTh6', 64.4, 467.60, 312, 201, 145890.30, 'WIF,BONK,POPCAT,MEW,TRUMP')
        ]

        for whale in whales:
            cur.execute("""
                INSERT OR REPLACE INTO tracked_wallets
                (address, win_rate, avg_pnl, total_trades, successful_trades, total_pnl,
                 first_seen, last_updated, is_active, tokens_traded)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now', '-30 days'), datetime('now'), 1, ?)
            """, whale)

        conn.commit()
        conn.close()

        logger.info("✅ Railway initialization complete")
        return {
            "success": True,
            "message": "Database initialized",
            "whales_seeded": len(whales)
        }

    except Exception as e:
        logger.error(f"Initialization error: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/aura/load_trackers")
async def load_all_trackers():
    """Load all 481 CT monitors and 154 whale wallets"""
    try:
        import subprocess
        result = subprocess.run(
            ["python3", "LOAD_ALL_TRACKERS_BATCH.py"],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            return {
                "success": True,
                "message": "All trackers loaded successfully",
                "output": result.stdout
            }
        else:
            return {
                "success": False,
                "error": result.stderr,
                "output": result.stdout
            }
    except Exception as e:
        logger.error(f"Tracker loading error: {e}")
        return {"success": False, "error": str(e)}

# Dashboard data endpoints
@app.get("/api/aura/signals")
async def get_signals(hours: int = 24, limit: int = 50):
    """Get recent Telegram signals from helix_signals table"""
    try:
        import sqlite3
        import json
        conn = sqlite3.connect('aura.db', timeout=10)
        cur = conn.cursor()

        # Check if table exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='helix_signals'")
        if not cur.fetchone():
            logger.warning("helix_signals table does not exist")
            conn.close()
            return {"signals": [], "count": 0}

        # Get signals from last N hours
        cur.execute("""
            SELECT token_address, symbol, momentum_score, market_cap, liquidity,
                   volume_24h, price, timestamp, metadata
            FROM helix_signals
            WHERE datetime(timestamp) > datetime('now', '-' || ? || ' hours')
            ORDER BY timestamp DESC
            LIMIT ?
        """, (hours, limit))

        signals = []
        for row in cur.fetchall():
            metadata = json.loads(row[8]) if row[8] else {}
            signals.append({
                'address': row[0],
                'symbol': row[1],
                'momentum': row[2],
                'mcap': row[3],
                'liquidity': row[4],
                'volume': row[5],
                'price': row[6],
                'timestamp': row[7],
                'risk_score': metadata.get('risk_score', 0),
                'narrative': metadata.get('narrative', ''),
                'strategy': metadata.get('strategy', '')
            })

        conn.close()
        logger.info(f"✅ Returning {len(signals)} signals")
        return {"signals": signals, "count": len(signals)}
    except Exception as e:
        logger.error(f"❌ Signals API error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"error": str(e), "signals": [], "count": 0}

@app.get("/api/aura/scanner/signals")
async def get_scanner_signals(hours: int = 24, limit: int = 50):
    """Get recent scanner signals (alias for /api/aura/signals)"""
    return await get_signals(hours, limit)

@app.get("/api/aura/wallets")
async def get_tracked_wallets():
    """Get tracked whale wallets - returns ALL wallets from database"""
    try:
        import sqlite3
        conn = sqlite3.connect('aura.db', timeout=10)
        cur = conn.cursor()

        # First check which table exists and has data
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('live_whale_wallets', 'tracked_wallets')")
        tables = [row[0] for row in cur.fetchall()]
        logger.info(f"Available wallet tables: {tables}")

        wallets = []

        # Try live_whale_wallets first
        if 'live_whale_wallets' in tables:
            cur.execute("SELECT COUNT(*) FROM live_whale_wallets")
            count = cur.fetchone()[0]
            logger.info(f"live_whale_wallets has {count} rows")

            if count > 0:
                cur.execute("""
                    SELECT wallet_address, nickname, min_tx_value_usd, total_alerts_sent, added_at
                    FROM live_whale_wallets
                    ORDER BY total_alerts_sent DESC
                """)

                for row in cur.fetchall():
                    wallets.append({
                        'address': row[0],
                        'nickname': row[1] or 'Unknown Whale',
                        'min_tx': row[2] or 10000,
                        'alerts': row[3] or 0,
                        'added': row[4],
                        'win_rate': 0,
                        'total_trades': 0
                    })

        # If no wallets found, try tracked_wallets
        if not wallets and 'tracked_wallets' in tables:
            cur.execute("SELECT COUNT(*) FROM tracked_wallets")
            count = cur.fetchone()[0]
            logger.info(f"tracked_wallets has {count} rows")

            if count > 0:
                cur.execute("""
                    SELECT address, win_rate, avg_pnl, total_trades, successful_trades,
                           total_pnl, last_updated, tokens_traded
                    FROM tracked_wallets
                    WHERE is_active = 1
                    ORDER BY total_pnl DESC
                """)

                for row in cur.fetchall():
                    wallets.append({
                        'address': row[0],
                        'nickname': 'Whale',
                        'win_rate': row[1],
                        'avg_pnl': row[2],
                        'total_trades': row[3],
                        'successful_trades': row[4],
                        'total_pnl': row[5],
                        'last_updated': row[6],
                        'tokens_traded': row[7].split(',') if row[7] else []
                    })

        conn.close()
        logger.info(f"✅ Returning {len(wallets)} wallets to frontend")
        return {"wallets": wallets, "count": len(wallets)}
    except Exception as e:
        logger.error(f"❌ Wallets API error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"error": str(e), "wallets": [], "count": 0}

@app.get("/api/aura/portfolio")
async def get_aura_portfolio():
    """Get portfolio summary"""
    try:
        from aura.database import db
        portfolio = db.get_portfolio_summary()
        positions = db.get_open_positions()
        return {
            "portfolio": portfolio,
            "positions": positions,
            "count": len(positions)
        }
    except Exception as e:
        logger.error(f"Portfolio API error: {e}")
        return {"error": str(e), "portfolio": {}, "positions": [], "count": 0}

# Logs API endpoint
@app.get("/api/aura/logs")
async def get_logs(limit: int = 100):
    """Get recent system logs"""
    try:
        log_file = "momentum_scanner.log"
        if not os.path.exists(log_file):
            return {"logs": [], "count": 0}

        with open(log_file, 'r') as f:
            lines = f.readlines()[-limit:]

        logs = []
        for line in lines:
            # Parse log format: 2025-10-06 18:30:45,123 - INFO - Message
            try:
                parts = line.split(' - ', 2)
                if len(parts) >= 3:
                    timestamp = parts[0].split(',')[0]  # Remove milliseconds
                    level = parts[1].strip().lower()
                    message = parts[2].strip()
                    logs.append({
                        'timestamp': timestamp,
                        'level': level,
                        'message': message
                    })
            except:
                continue

        return {"logs": logs, "count": len(logs)}
    except Exception as e:
        logger.error(f"Logs API error: {e}")
        return {"error": str(e), "logs": [], "count": 0}

# Social Momentum API endpoint
@app.get("/api/aura/social/momentum")
async def get_social_momentum():
    """Get trending tokens from social media"""
    # TODO: Integrate with Twitter API or social sentiment service
    # For now, return mock data showing trending Solana tokens
    return {
        "trends": [
            {
                "symbol": "BONK",
                "mentions": 1234,
                "sentiment": 0.75,
                "change_24h": 15.3,
                "volume_24h": 1500000
            },
            {
                "symbol": "WIF",
                "mentions": 987,
                "sentiment": 0.82,
                "change_24h": 22.1,
                "volume_24h": 980000
            },
            {
                "symbol": "JUP",
                "mentions": 856,
                "sentiment": 0.68,
                "change_24h": -5.2,
                "volume_24h": 2100000
            },
            {
                "symbol": "PYTH",
                "mentions": 743,
                "sentiment": 0.71,
                "change_24h": 8.7,
                "volume_24h": 890000
            }
        ],
        "count": 4,
        "last_updated": datetime.now().isoformat()
    }

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
        voice = message.get('voice')
        user_id = message.get('from', {}).get('id', 0)
        username = message.get('from', {}).get('username') or message.get('from', {}).get('first_name', 'User')

        if not chat_id:
            return {"ok": True}

        # Handle voice messages
        if voice and not text:
            logger.info(f"🎤 Voice message from {username} ({chat_id})")

            # Try to transcribe using OpenAI Whisper
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                try:
                    import tempfile
                    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

                    # Get voice file
                    async with aiohttp.ClientSession() as session:
                        file_url = f"https://api.telegram.org/bot{bot_token}/getFile?file_id={voice['file_id']}"
                        async with session.get(file_url) as resp:
                            file_info = await resp.json()
                            file_path = file_info['result']['file_path']

                        # Download voice file
                        voice_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
                        async with session.get(voice_url) as resp:
                            voice_data = await resp.read()

                    # Save temporarily
                    with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as tmp:
                        tmp.write(voice_data)
                        tmp_path = tmp.name

                    # Transcribe with Whisper
                    from openai import OpenAI
                    client = OpenAI(api_key=openai_key)
                    with open(tmp_path, 'rb') as audio_file:
                        transcript = client.audio.transcriptions.create(
                            model="whisper-1",
                            file=audio_file
                        )
                        text = transcript.text

                    # Clean up
                    os.unlink(tmp_path)

                    logger.info(f"📝 Transcribed: {text[:50]}...")

                    # Send transcription confirmation
                    async with aiohttp.ClientSession() as session:
                        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                        await session.post(url, json={
                            "chat_id": chat_id,
                            "text": f"🎤 Transcribed: _{text}_",
                            "parse_mode": "Markdown"
                        })

                except Exception as e:
                    logger.error(f"Whisper transcription error: {e}")
                    text = "voice message (transcription failed)"
            else:
                text = "voice message (no OpenAI key)"

        if not text:
            return {"ok": True}

        logger.info(f"📱 Message from {username} ({chat_id}): {text[:100]}")

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
                    response_text += f"• {symbol} - Momentum: {momentum:.1f}\n"
                response_text += "\nUse /signals for full list"
            else:
                response_text += "No recent signals"

        # FULL CONVERSATIONAL AI - Claude Integration
        else:
            # Use Claude for natural conversation
            try:
                import anthropic
                anthropic_key = os.getenv("ANTHROPIC_API_KEY")

                if not anthropic_key:
                    # Fallback to OpenAI if no Anthropic key
                    openai_key = os.getenv("OPENAI_API_KEY")
                    if openai_key:
                        from openai import OpenAI
                        client = OpenAI(api_key=openai_key)

                        system_context = f"""You are AURA, an autonomous trading intelligence system for Solana memecoins.

Current Portfolio Status:
- Open Positions: {portfolio['open_positions']}
- Total P&L: ${portfolio['total_pnl_usd']:.2f} ({portfolio['total_pnl_percent']:+.1f}%)
- Win Rate: {portfolio['win_rate']:.1f}%

Recent Signals: {len(signals)} in last 24h
Watchlist: {len(watchlist)} tokens

You can discuss:
- Trading strategies and market analysis
- Portfolio performance and risk management
- Recent signals and token opportunities
- Technical questions about Solana/DeFi
- System status and deployment

Respond naturally and helpfully. Keep responses concise (2-4 sentences). Use emojis sparingly."""

                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": system_context},
                                {"role": "user", "content": text}
                            ],
                            max_tokens=300,
                            temperature=0.7
                        )

                        response_text = response.choices[0].message.content
                        logger.info(f"🤖 GPT-4o-mini response generated")
                    else:
                        response_text = "🤖 I can help with:\n\n"
                        response_text += "Trading: /portfolio /signals /watchlist\n"
                        response_text += "System: /status /deploy /changes\n\n"
                        response_text += "Natural conversation requires ANTHROPIC_API_KEY or OPENAI_API_KEY"
                else:
                    # Use Claude (preferred)
                    client = anthropic.Anthropic(api_key=anthropic_key)

                    system_context = f"""You are AURA, an autonomous trading intelligence system for Solana memecoins.

Current Portfolio Status:
- Open Positions: {portfolio['open_positions']}
- Total P&L: ${portfolio['total_pnl_usd']:.2f} ({portfolio['total_pnl_percent']:+.1f}%)
- Win Rate: {portfolio['win_rate']:.1f}%

Recent Signals: {len(signals)} in last 24h
Watchlist: {len(watchlist)} tokens

You can discuss:
- Trading strategies and market analysis
- Portfolio performance and risk management
- Recent signals and token opportunities
- Technical questions about Solana/DeFi
- System status and deployment

Respond naturally and helpfully. Keep responses concise (2-4 sentences) formatted for Telegram. Use emojis sparingly."""

                    message = client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=300,
                        system=system_context,
                        messages=[
                            {"role": "user", "content": text}
                        ]
                    )

                    response_text = message.content[0].text
                    logger.info(f"🤖 Claude response generated")

            except Exception as e:
                logger.error(f"AI response error: {e}")
                response_text = f"🤖 I understand you're asking about: _{text}_\n\n"
                response_text += "I can help with:\n"
                response_text += "• /portfolio - View positions\n"
                response_text += "• /signals - Recent opportunities\n"
                response_text += "• /status - System status\n\n"
                response_text += "For full AI chat, set ANTHROPIC_API_KEY or OPENAI_API_KEY"

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
