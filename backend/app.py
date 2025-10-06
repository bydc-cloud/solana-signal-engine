"""FastAPI backend for copy-trade orchestration.

Expose REST endpoints that receive smart wallet events, log trades,
relay to external services (Coinrule/Telegram/Sheets/Notion), and
serve data for dashboards such as Lovable.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("copytrade")

# ---------------------------------------------------------------------------
# Environment / configuration
# ---------------------------------------------------------------------------
MODE = os.getenv("MODE", "PAPER").upper()
START_EQUITY = float(os.getenv("START_EQUITY_USD", "100000"))
MAX_RISK_PCT = float(os.getenv("MAX_RISK_PER_TRADE_PCT", "0.01"))
COPYTRADE_WALLETS = set()
try:
    COPYTRADE_WALLETS = set(json.loads(os.getenv("COPYTRADE_WALLETS", "[]")))
except json.JSONDecodeError:
    logger.warning("COPYTRADE_WALLETS env variable is not valid JSON.")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///../final_nuclear.db")
API_TOKEN = os.getenv("COPYTRADE_API_TOKEN")

engine = create_engine(DATABASE_URL, future=True, echo=False)

# ---------------------------------------------------------------------------
# Helper models / utilities
# ---------------------------------------------------------------------------
class SmartWalletEvent(BaseModel):
    wallet: str = Field(..., description="Wallet address that triggered the event")
    tokenSymbol: str = Field(..., description="Token symbol")
    tokenAddress: str = Field(..., description="Token mint address")
    action: str = Field("buy", description="buy or sell")
    amountUsd: float = Field(0.0, description="USD notional the wallet traded")
    walletTag: Optional[str] = Field(None, description="Optional label for the wallet")
    metadata: Dict[str, Any] = Field(default_factory=dict)


def compute_size(usd_amount: float) -> float:
    """Return the USD size we will mirror for the trade."""
    max_size = START_EQUITY * MAX_RISK_PCT
    if usd_amount <= 0:
        return max_size
    return min(max_size, usd_amount)


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_tables() -> None:
    """Create append-only tables if they do not exist yet."""
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS copytrade_trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    wallet TEXT,
                    wallet_tag TEXT,
                    token_symbol TEXT,
                    token_address TEXT,
                    action TEXT,
                    mode TEXT,
                    size_usd REAL,
                    reason TEXT,
                    raw JSON
                )
                """
            )
        )


_ensure_tables()


async def submit_coinrule(trade: Dict[str, Any]) -> None:
    """Stub: send trade to Coinrule webhook.

    Replace with requests.post(COINRULE_WEBHOOK_URL, json=payload).
    """
    url = os.getenv("COINRULE_WEBHOOK_URL")
    if not url:
        logger.info("Coinrule webhook not configured; skipping for %s", trade["tokenSymbol"])
        return
    import aiohttp

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=trade, timeout=10) as resp:
                if resp.status >= 300:
                    body = await resp.text()
                    logger.error("Coinrule webhook failed (%s): %s", resp.status, body)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Coinrule webhook error: %s", exc)


def record_trade(trade: Dict[str, Any]) -> None:
    """Persist trade to the local database."""
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO copytrade_trades (
                        wallet, wallet_tag, token_symbol, token_address,
                        action, mode, size_usd, reason, raw
                    ) VALUES (:wallet, :wallet_tag, :token_symbol, :token_address,
                             :action, :mode, :size_usd, :reason, :raw)
                    """
                ),
                {
                    "wallet": trade["wallet"],
                    "wallet_tag": trade.get("walletTag"),
                    "token_symbol": trade["tokenSymbol"],
                    "token_address": trade["tokenAddress"],
                    "action": trade["action"],
                    "mode": trade["mode"],
                    "size_usd": trade["sizeUsd"],
                    "reason": trade.get("reason"),
                    "raw": json.dumps(trade),
                },
            )
    except SQLAlchemyError as exc:  # noqa: BLE001
        logger.exception("Failed to insert trade record: %s", exc)


async def send_telegram(trade: Dict[str, Any]) -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        logger.info("Telegram credentials missing; skipping alert.")
        return

    text = (
        f"*COPY TRADE* ${trade['tokenSymbol']} — {trade['action']}\n"
        f"Wallet: `{trade['wallet']}`\n"
        f"Mode: {trade['mode']} | Size: ${trade['sizeUsd']:.2f}\n"
        f"Reason: {trade.get('reason', 'copy trade')}"
    )

    import aiohttp

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, timeout=10) as resp:
                if resp.status >= 300:
                    body = await resp.text()
                    logger.error("Telegram send failed (%s): %s", resp.status, body)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Telegram error: %s", exc)


async def log_to_google_sheet(trade: Dict[str, Any]) -> None:  # pragma: no cover - optional
    if not os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID"):
        return
    # TODO: implement Google Sheets append


async def log_to_notion(trade: Dict[str, Any]) -> None:  # pragma: no cover - optional
    if not os.getenv("NOTION_API_KEY"):
        return
    # TODO: implement Notion logging


async def verify_auth(x_api_token: Optional[str] = Header(None)) -> None:
    if API_TOKEN and x_api_token != API_TOKEN:
        raise HTTPException(status_code=401, detail="invalid token")


app = FastAPI(title="CopyTrade Controller")


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok", "mode": MODE, "wallets": str(len(COPYTRADE_WALLETS))}


@app.post("/webhook/smart-wallet")
async def smart_wallet(event: SmartWalletEvent, _: None = Depends(verify_auth)) -> Dict[str, Any]:
    action = event.action.upper()
    if event.wallet not in COPYTRADE_WALLETS:
        logger.debug("Ignoring wallet %s", event.wallet)
        return {"status": "ignored"}

    trade = {
        "ts": now_utc(),
        "wallet": event.wallet,
        "walletTag": event.walletTag or "smart",
        "tokenSymbol": event.tokenSymbol,
        "tokenAddress": event.tokenAddress,
        "action": action,
        "mode": MODE,
        "sizeUsd": compute_size(event.amountUsd),
        "reason": event.metadata.get("reason")
        or f"Copy trade {event.walletTag or event.wallet}",
        "metadata": event.metadata,
    }

    logger.info("Processing %s of %s by %s", action, event.tokenSymbol, event.wallet)

    if action == "BUY":
        await submit_coinrule(trade)
        await send_telegram(trade)
        record_trade(trade)
        await asyncio.gather(log_to_google_sheet(trade), log_to_notion(trade))
    elif action == "SELL":
        await submit_coinrule(trade)
        await send_telegram(trade)
        record_trade(trade)
        await asyncio.gather(log_to_google_sheet(trade), log_to_notion(trade))

    return {"status": "processed", "mode": MODE}


@app.post("/control/add-wallet")
async def add_wallet(payload: Dict[str, str], _: None = Depends(verify_auth)) -> Dict[str, Any]:
    wallet = payload.get("wallet")
    if not wallet:
        raise HTTPException(status_code=400, detail="wallet missing")
    COPYTRADE_WALLETS.add(wallet)
    logger.info("Wallet %s added to copytrade list", wallet)
    return {"status": "ok", "wallets": sorted(COPYTRADE_WALLETS)}


@app.post("/control/remove-wallet")
async def remove_wallet(payload: Dict[str, str], _: None = Depends(verify_auth)) -> Dict[str, Any]:
    wallet = payload.get("wallet")
    if not wallet:
        raise HTTPException(status_code=400, detail="wallet missing")
    COPYTRADE_WALLETS.discard(wallet)
    logger.info("Wallet %s removed from copytrade list", wallet)
    return {"status": "ok", "wallets": sorted(COPYTRADE_WALLETS)}


@app.get("/reports/trades")
async def trades_report(_: None = Depends(verify_auth)) -> Dict[str, Any]:
    with engine.begin() as conn:
        rows = conn.execute(
            text(
                """
                SELECT ts, wallet, wallet_tag, token_symbol, action, mode, size_usd, reason
                FROM copytrade_trades
                ORDER BY ts DESC
                LIMIT 100
                """
            )
        ).fetchall()
    return {
        "mode": MODE,
        "trades": [
            {
                "ts": row.ts,
                "wallet": row.wallet,
                "walletTag": row.wallet_tag,
                "tokenSymbol": row.token_symbol,
                "action": row.action,
                "mode": row.mode,
                "sizeUsd": row.size_usd,
                "reason": row.reason,
            }
            for row in rows
        ],
    }
