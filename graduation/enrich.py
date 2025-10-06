"""Data enrichment for Graduation candidates."""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, Dict, Optional

import aiohttp

from .types import EnrichedCandidate, GraduationCandidateSeed

logger = logging.getLogger(__name__)

BIRDEYE_TOKEN_URL = "https://public-api.birdeye.so/defi/token_overview"
BIRDEYE_TRADE_URL = "https://public-api.birdeye.so/defi/token_trades"
HELIUS_TOKEN_URL = "https://api.helius.xyz/v0/tokens/metadata"
RUGCHECK_URL = "https://api.rugcheck.xyz/v1/tokens/"
GMGN_HOLDERS_URL = "https://gmgn.ai/api/v1/token/holders"
SOLSCAN_ACCOUNT_URL = "https://public-api.solscan.io/token/meta"
NASEN_SMARTMONEY_URL = "https://api.nasen.ai/v1/smart-money/token"


async def enrich_candidate(seed: GraduationCandidateSeed) -> EnrichedCandidate:
    birdeye_key = os.getenv("BIRDEYE_API_KEY")
    helius_key = os.getenv("HELIUS_API_KEY")
    nasen_key = os.getenv("NASEN_API_KEY")

    async with aiohttp.ClientSession() as session:
        birdeye_task = asyncio.create_task(_fetch_birdeye(session, birdeye_key, seed.address))
        helius_task = asyncio.create_task(_fetch_helius(session, helius_key, seed.address))
        rug_task = asyncio.create_task(_fetch_rugcheck(session, seed.address))
        holders_task = asyncio.create_task(_fetch_holders(session, seed.address))
        solscan_task = asyncio.create_task(_fetch_solscan(session, seed.address))
        nasen_task = asyncio.create_task(_fetch_nasen(session, nasen_key, seed.address))

        birdeye = await birdeye_task
        helius_meta = await helius_task
        rugcheck = await rug_task
        holders = await holders_task
        solscan = await solscan_task
        nasen = await nasen_task

    market = _build_market_snapshot(seed, birdeye)
    onchain = _build_onchain_snapshot(seed, helius_meta, solscan)
    risk = _build_risk_snapshot(seed, rugcheck, holders, onchain)
    analytics = _build_analytics(seed, birdeye, holders, nasen)

    return EnrichedCandidate(
        seed=seed,
        market=market,
        onchain=onchain,
        risk=risk,
        analytics=analytics,
    )


async def _fetch_birdeye(session: aiohttp.ClientSession, api_key: Optional[str], address: str) -> Dict[str, Any]:
    if not api_key:
        return {}

    headers = {"X-API-KEY": api_key, "x-chain": "solana"}
    params = {"address": address, "timeframe": "15m"}
    try:
        async with session.get(BIRDEYE_TOKEN_URL, headers=headers, params=params, timeout=8) as resp:
            if resp.status != 200:
                logger.debug("Birdeye overview error %s", resp.status)
                return {}
            overview = await resp.json()
    except Exception as exc:
        logger.debug("Birdeye overview failure: %s", exc)
        overview = {}

    try:
        trade_params = {"address": address, "limit": 100}
        async with session.get(BIRDEYE_TRADE_URL, headers=headers, params=trade_params, timeout=8) as resp:
            if resp.status != 200:
                return {"overview": overview}
            trades = await resp.json()
    except Exception as exc:
        logger.debug("Birdeye trades failure: %s", exc)
        trades = {}

    return {"overview": overview, "trades": trades}


async def _fetch_helius(session: aiohttp.ClientSession, api_key: Optional[str], address: str) -> Dict[str, Any]:
    if not api_key:
        return {}
    url = f"{HELIUS_TOKEN_URL}?api-key={api_key}"
    payload = {"mintAccounts": [address]}
    try:
        async with session.post(url, json=payload, timeout=8) as resp:
            if resp.status != 200:
                logger.debug("Helius metadata error %s", resp.status)
                return {}
            data = await resp.json()
            if isinstance(data, list) and data:
                return data[0]
    except Exception as exc:
        logger.debug("Helius metadata failure: %s", exc)
    return {}


async def _fetch_rugcheck(session: aiohttp.ClientSession, address: str) -> Dict[str, Any]:
    url = f"{RUGCHECK_URL}{address}"
    try:
        async with session.get(url, timeout=6) as resp:
            if resp.status != 200:
                return {}
            return await resp.json()
    except Exception:
        return {}


async def _fetch_holders(session: aiohttp.ClientSession, address: str) -> Dict[str, Any]:
    params = {"address": address, "chain": "solana"}
    try:
        async with session.get(GMGN_HOLDERS_URL, params=params, timeout=6) as resp:
            if resp.status != 200:
                return {}
            return await resp.json()
    except Exception:
        return {}


async def _fetch_solscan(session: aiohttp.ClientSession, address: str) -> Dict[str, Any]:
    params = {"tokenAddress": address}
    try:
        async with session.get(SOLSCAN_ACCOUNT_URL, params=params, timeout=6) as resp:
            if resp.status != 200:
                return {}
            return await resp.json()
    except Exception:
        return {}


async def _fetch_nasen(session: aiohttp.ClientSession, api_key: Optional[str], address: str) -> Dict[str, Any]:
    if not api_key:
        return {}

    headers = {"NASEN-API-KEY": api_key}
    params = {"chain": "solana", "token": address}
    try:
        async with session.get(NASEN_SMARTMONEY_URL, headers=headers, params=params, timeout=6) as resp:
            if resp.status != 200:
                body = await resp.text()
                logger.debug("Nasen token error %s: %s", resp.status, body[:120])
                return {}
            return await resp.json()
    except Exception as exc:  # noqa: BLE001
        logger.debug("Nasen fetch failure for %s: %s", address, exc)
        return {}


def _build_market_snapshot(seed: GraduationCandidateSeed, birdeye: Dict[str, Any]) -> Dict[str, Any]:
    overview = birdeye.get("overview", {}).get("data", {})
    price = overview.get("price", 0.0)
    market_cap = overview.get("mc", 0.0)
    liquidity = overview.get("liquidity", 0.0)
    vol_15m = overview.get("v15mUSD", 0.0)
    buy_ratio = overview.get("buySellRatio", 0.0)

    return {
        "price": price,
        "market_cap": market_cap,
        "liquidity": liquidity,
        "vol_15m_usd": vol_15m,
        "buy_ratio_15m": buy_ratio,
        "pumpfun_curve_pct": seed.pumpfun_curve_pct,
    }


def _build_onchain_snapshot(seed: GraduationCandidateSeed, helius_meta: Dict[str, Any], solscan: Dict[str, Any]) -> Dict[str, Any]:
    authorities = helius_meta.get("token_info", {}).get("authority") if helius_meta else {}
    freeze_authority = authorities.get("freeze") if isinstance(authorities, dict) else None
    mint_authority = authorities.get("mint") if isinstance(authorities, dict) else None

    lock_info = solscan.get("lockUp") if isinstance(solscan, dict) else None
    locker_address = None
    lock_days = 0
    if isinstance(lock_info, dict):
        locker_address = lock_info.get("address")
        lock_seconds = lock_info.get("lockTime") or 0
        lock_days = round(lock_seconds / 86400, 2) if lock_seconds else 0

    return {
        "mint_authority": mint_authority,
        "freeze_authority": freeze_authority,
        "locker_address": locker_address,
        "lock_days": lock_days,
        "supply": helius_meta.get("token_info", {}).get("supply"),
    }


def _build_risk_snapshot(seed: GraduationCandidateSeed, rugcheck: Dict[str, Any], holders: Dict[str, Any], onchain: Dict[str, Any]) -> Dict[str, Any]:
    sellable = rugcheck.get("sellable", True)
    sniper_pct = 0.0
    top10_pct = 0.0
    insiders_pct = 0.0
    holder_velocity = 0.0

    if holders:
        stats = holders.get("data") or holders
        sniper_pct = float(stats.get("sniperPct", 0.0) or 0.0)
        top10_pct = float(stats.get("top10HolderPct", 0.0) or 0.0)
        insiders_pct = float(stats.get("insiderPct", 0.0) or 0.0)
        holder_velocity = float(stats.get("holderVelocity", 0.0) or 0.0)

    creator_info = rugcheck.get("creator", {}) if isinstance(rugcheck, dict) else {}
    creator_address = creator_info.get("address")
    creator_rugs_90d = creator_info.get("rugs90d", 0)
    creator_success_10x = creator_info.get("success10x", 0)

    return {
        "sellability_sim_ok": bool(rugcheck.get("sellable", sellable)),
        "sellability_context": rugcheck.get("reason"),
        "mint_revoked": rugcheck.get("mintAuthorityRenounced", onchain.get("mint_authority") is None),
        "freeze_revoked": rugcheck.get("freezeAuthorityRenounced", onchain.get("freeze_authority") is None),
        "lp_locked_bool": bool(rugcheck.get("lpLocked", onchain.get("lock_days", 0) > 0)),
        "lock_days": onchain.get("lock_days", 0),
        "locker_address": onchain.get("locker_address"),
        "locker_rep_score": float(rugcheck.get("lockerRepScore", 0.0) or 0.0),
        "sniper_pct": sniper_pct,
        "top10_pct": top10_pct,
        "insider_pct": insiders_pct,
        "holder_velocity": holder_velocity,
        "creator_address": creator_address,
        "creator_flagged_rugs": creator_rugs_90d or 0,
        "creator_success_10x": creator_success_10x or 0,
        "creator_blocklisted": bool(rugcheck.get("isScam", False)),
    }


def _build_analytics(
    seed: GraduationCandidateSeed,
    birdeye: Dict[str, Any],
    holders: Dict[str, Any],
    nasen: Dict[str, Any],
) -> Dict[str, Any]:
    trades = birdeye.get("trades", {}).get("data", [])
    buy_trades = [t for t in trades if t.get("side") == "buy"]
    sell_trades = [t for t in trades if t.get("side") == "sell"]
    buy_volume = sum(t.get("quoteAmount", 0.0) for t in buy_trades)
    sell_volume = sum(t.get("quoteAmount", 0.0) for t in sell_trades)
    trades_ts = [t.get("blockUnixTime", 0) for t in trades]
    last_trade_age = None
    if trades_ts:
        last_trade_age = max(trades_ts)
    holder_stats = holders.get("data") or holders
    whales_inflow = float(holder_stats.get("whaleInflow", 0.0) or 0.0)

    nasen_data = nasen.get("data") or nasen or {}
    smart_money = nasen_data.get("smart_money") or nasen_data.get("smartMoney") or {}
    nasen_active_wallets = smart_money.get("active_wallets") or smart_money.get("activeWallets")
    nasen_net_flow = smart_money.get("netflow_usd") or smart_money.get("netFlowUsd")
    nasen_buy_usd = smart_money.get("buy_usd") or smart_money.get("buyUsd")
    nasen_sell_usd = smart_money.get("sell_usd") or smart_money.get("sellUsd")
    nasen_unique_wallets = smart_money.get("unique_wallets") or smart_money.get("uniqueWallets")

    return {
        "buy_volume": buy_volume,
        "sell_volume": sell_volume,
        "buyers": len(buy_trades),
        "sellers": len(sell_trades),
        "last_trade_ts": last_trade_age,
        "whales_inflow": whales_inflow,
        "trade_samples": len(trades),
        "nasen_active_wallets": nasen_active_wallets,
        "nasen_net_flow_usd": nasen_net_flow,
        "nasen_buy_usd": nasen_buy_usd,
        "nasen_sell_usd": nasen_sell_usd,
        "nasen_unique_wallets": nasen_unique_wallets,
    }
