"""
Helix Trading Bot API Server
FastAPI server for Lovable AI control center integration
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import sqlite3
import json
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

app = FastAPI(title="Helix Trading Bot API", version="1.0.0")

# Enable CORS for Lovable frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Lovable app domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = Path(__file__).parent / "final_nuclear.db"
SCANNER_PID_PATH = Path(__file__).parent / "scanner.pid"


class ConfigUpdate(BaseModel):
    key: str
    value: str


class TradeFilter(BaseModel):
    hours: Optional[int] = 24
    mode: Optional[str] = None  # PAPER or LIVE
    min_gs: Optional[float] = None


# ============================================================================
# SCANNER CONTROL ENDPOINTS
# ============================================================================

def load_scanner_metrics():
    """
    Load scanner metrics from data/scanner_metrics.json
    Gracefully falls back to defaults if file missing or invalid
    """
    metrics_path = Path(__file__).parent / "data" / "scanner_metrics.json"
    default_metrics = {
        'cycles': 0,
        'signals': 0,
        'watchlist_alerts': 0,
        'empty_cycles': 0,
        'avg_cycle_seconds': 0.0,
        'last_cycle_seconds': 0.0,
    }

    if not metrics_path.exists():
        return default_metrics

    try:
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
            # Validate all expected keys present
            for key in default_metrics:
                if key not in metrics:
                    metrics[key] = default_metrics[key]
            return metrics
    except (json.JSONDecodeError, IOError) as e:
        import logging
        logging.warning(f"Failed to load scanner metrics from {metrics_path}: {e}")
        return default_metrics


@app.get("/status")
async def get_status():
    """Get overall bot status with scanner metrics"""
    try:
        # Check if scanner is running
        scanner_running = False
        scanner_pid = None
        if SCANNER_PID_PATH.exists():
            with open(SCANNER_PID_PATH) as f:
                scanner_pid = f.read().strip()
            # Check if process is actually running
            try:
                result = subprocess.run(
                    ["ps", "-p", scanner_pid],
                    capture_output=True,
                    text=True
                )
                scanner_running = scanner_pid in result.stdout
            except Exception:
                scanner_running = False

        # Get paper equity
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT equity_usd, realized_pnl_usd, unrealized_pnl_usd
                FROM grad_paper_equity
                ORDER BY ts DESC LIMIT 1
            """)
            equity_row = cur.fetchone()

            # Count recent trades
            cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
            cur.execute("SELECT COUNT(*) FROM trades WHERE created_at >= ?", (cutoff,))
            trades_24h = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM alerts WHERE created_at >= ?", (cutoff,))
            alerts_24h = cur.fetchone()[0]

        # Load scanner metrics
        scanner_metrics = load_scanner_metrics()

        return {
            "scanner_running": scanner_running,
            "scanner_pid": scanner_pid if scanner_running else None,
            "scanner_status": "running" if scanner_running else "stopped",
            "database_initialized": DB_PATH.exists(),
            "paper_equity": {
                "total_usd": round(equity_row[0], 2) if equity_row else 100000,
                "realized_pnl": round(equity_row[1], 2) if equity_row and equity_row[1] else 0,
                "unrealized_pnl": round(equity_row[2], 2) if equity_row and equity_row[2] else 0,
            },
            "stats_24h": {
                "trades": trades_24h,
                "alerts": alerts_24h,
            },
            "scanner_metrics": {
                "cycles": scanner_metrics['cycles'],
                "signals": scanner_metrics['signals'],
                "watchlist_alerts": scanner_metrics['watchlist_alerts'],
                "empty_cycles": scanner_metrics['empty_cycles'],
                "avg_cycle_seconds": round(scanner_metrics['avg_cycle_seconds'], 2),
                "last_cycle_seconds": round(scanner_metrics['last_cycle_seconds'], 2),
            },
            "mode": os.getenv("GRAD_MODE", "PAPER"),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scanner/start")
async def start_scanner(background_tasks: BackgroundTasks):
    """Start the scanner"""
    try:
        result = subprocess.run(
            ["./RUN_AUTONOMOUS.sh"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True
        )
        return {
            "success": True,
            "message": "Scanner started",
            "output": result.stdout
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scanner/stop")
async def stop_scanner():
    """Stop the scanner"""
    try:
        subprocess.run(["pkill", "-f", "REALITY_MOMENTUM_SCANNER.py"])
        return {"success": True, "message": "Scanner stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scanner/restart")
async def restart_scanner(background_tasks: BackgroundTasks):
    """Restart the scanner"""
    try:
        # Stop
        subprocess.run(["pkill", "-f", "REALITY_MOMENTUM_SCANNER.py"])
        # Wait a bit
        import time
        time.sleep(2)
        # Start
        result = subprocess.run(
            ["./RUN_AUTONOMOUS.sh"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True
        )
        return {
            "success": True,
            "message": "Scanner restarted",
            "output": result.stdout
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scanner/metrics")
async def get_scanner_metrics():
    """
    Get detailed scanner metrics
    Exposes cycles, signals, empty_cycles, avg_cycle_seconds, last_cycle_seconds
    """
    try:
        metrics = load_scanner_metrics()
        return {
            "cycles": metrics['cycles'],
            "signals": metrics['signals'],
            "watchlist_alerts": metrics['watchlist_alerts'],
            "empty_cycles": metrics['empty_cycles'],
            "last_cycle_seconds": round(metrics['last_cycle_seconds'], 3),
            "avg_cycle_seconds": round(metrics['avg_cycle_seconds'], 3),
            "last_updated": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# TRADING DATA ENDPOINTS
# ============================================================================

@app.get("/trades")
async def get_trades(hours: int = 24, mode: Optional[str] = None, limit: int = 50):
    """Get recent trades"""
    try:
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()

        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()

            query = """
                SELECT
                    t.token_address,
                    t.created_at,
                    t.grad_size_fraction,
                    t.grad_route,
                    t.metadata,
                    a.grad_gs,
                    a.payload
                FROM trades t
                LEFT JOIN alerts a ON t.token_address = a.token_address
                WHERE t.created_at >= ?
            """

            if mode:
                query += " AND json_extract(t.metadata, '$.mode') = ?"
                cur.execute(query + " ORDER BY t.created_at DESC LIMIT ?", (cutoff, mode, limit))
            else:
                cur.execute(query + " ORDER BY t.created_at DESC LIMIT ?", (cutoff, limit))

            trades = []
            for row in cur.fetchall():
                try:
                    meta = json.loads(row[4]) if row[4] else {}
                    payload = json.loads(row[6]) if row[6] else {}
                    trades.append({
                        "address": row[0],
                        "created_at": row[1],
                        "size_fraction": row[2],
                        "route": row[3],
                        "mode": meta.get("mode"),
                        "txid": meta.get("txid"),
                        "gs": row[5],
                        "symbol": payload.get("symbol"),
                    })
                except Exception:
                    continue

            return {"trades": trades, "count": len(trades)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/alerts")
async def get_alerts(hours: int = 24, min_gs: Optional[float] = None, limit: int = 100):
    """Get recent alerts"""
    try:
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()

        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()

            query = """
                SELECT
                    token_address,
                    created_at,
                    grad_gs,
                    payload,
                    grad_mode
                FROM alerts
                WHERE created_at >= ?
            """

            if min_gs:
                query += " AND grad_gs >= ?"
                cur.execute(query + " ORDER BY grad_gs DESC LIMIT ?", (cutoff, min_gs, limit))
            else:
                cur.execute(query + " ORDER BY grad_gs DESC LIMIT ?", (cutoff, limit))

            alerts = []
            for row in cur.fetchall():
                try:
                    payload = json.loads(row[3]) if row[3] else {}
                    gates = payload.get("gates", {})

                    alerts.append({
                        "address": row[0],
                        "created_at": row[1],
                        "gs": row[2],
                        "symbol": payload.get("symbol", "UNKNOWN"),
                        "gates": gates,
                        "gate_passed": all(gates.values()) if gates else False,
                        "mode": row[4] or "PAPER",
                    })
                except Exception:
                    continue

            return {"alerts": alerts, "count": len(alerts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/daily")
async def get_daily_analytics():
    """Get daily analytics summary"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()

            # Last 7 days
            days_data = []
            for days_ago in range(7):
                date = datetime.now() - timedelta(days=days_ago)
                start = date.replace(hour=0, minute=0, second=0).isoformat()
                end = date.replace(hour=23, minute=59, second=59).isoformat()

                # Trades
                cur.execute("""
                    SELECT COUNT(*),
                           json_extract(metadata, '$.mode') as mode
                    FROM trades
                    WHERE created_at BETWEEN ? AND ?
                    GROUP BY mode
                """, (start, end))
                trade_counts = {row[1]: row[0] for row in cur.fetchall()}

                # Alerts
                cur.execute("""
                    SELECT COUNT(*), AVG(grad_gs)
                    FROM alerts
                    WHERE created_at BETWEEN ? AND ?
                """, (start, end))
                alert_row = cur.fetchone()

                days_data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "trades_paper": trade_counts.get("PAPER", 0),
                    "trades_live": trade_counts.get("LIVE", 0),
                    "alerts": alert_row[0] if alert_row else 0,
                    "avg_gs": round(alert_row[1], 2) if alert_row and alert_row[1] else 0,
                })

            return {"daily_stats": days_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/performance")
async def get_performance():
    """Get performance metrics"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()

            # Get equity history
            cur.execute("""
                SELECT ts, equity_usd, realized_pnl_usd, unrealized_pnl_usd
                FROM grad_paper_equity
                ORDER BY ts DESC
                LIMIT 100
            """)

            equity_history = [
                {
                    "timestamp": row[0],
                    "equity": round(row[1], 2),
                    "realized_pnl": round(row[2], 2) if row[2] else 0,
                    "unrealized_pnl": round(row[3], 2) if row[3] else 0,
                }
                for row in cur.fetchall()
            ]

            # Calculate stats
            if len(equity_history) > 1:
                start_equity = equity_history[-1]["equity"]
                current_equity = equity_history[0]["equity"]
                total_return = ((current_equity - start_equity) / start_equity) * 100
            else:
                total_return = 0

            return {
                "equity_history": equity_history,
                "total_return_pct": round(total_return, 2),
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# CONFIGURATION ENDPOINTS
# ============================================================================

@app.get("/config")
async def get_config():
    """Get current configuration"""
    try:
        config = {
            "GRAD_MODE": os.getenv("GRAD_MODE", "PAPER"),
            "GRAD_MIN_SCORE": os.getenv("GRAD_MIN_SCORE", "35"),
            "GRAD_PER_TRADE_CAP": os.getenv("GRAD_PER_TRADE_CAP", "0.02"),
            "GRAD_GLOBAL_EXPOSURE_CAP": os.getenv("GRAD_GLOBAL_EXPOSURE_CAP", "0.90"),
            "GRAD_MAX_CONCURRENT": os.getenv("GRAD_MAX_CONCURRENT", "20"),
        }
        return {"config": config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/config/update")
async def update_config(update: ConfigUpdate):
    """Update configuration (requires restart)"""
    try:
        # Read current .env
        env_path = Path(__file__).parent / ".env"
        with open(env_path) as f:
            lines = f.readlines()

        # Update or add the key
        found = False
        for i, line in enumerate(lines):
            if line.startswith(f"{update.key}="):
                lines[i] = f"{update.key}={update.value}\n"
                found = True
                break

        if not found:
            lines.append(f"{update.key}={update.value}\n")

        # Write back
        with open(env_path, 'w') as f:
            f.writelines(lines)

        return {
            "success": True,
            "message": f"Updated {update.key}. Restart scanner to apply.",
            "key": update.key,
            "value": update.value,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/logs")
async def get_logs(lines: int = 100):
    """Get recent scanner logs"""
    try:
        log_path = Path(__file__).parent / "momentum_scanner.log"
        if not log_path.exists():
            return {"logs": []}

        with open(log_path) as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:]

        return {"logs": recent_lines}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "Helix Trading Bot API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
