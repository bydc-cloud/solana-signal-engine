
"""Telegram notifications for Graduation candidates."""

from __future__ import annotations

import logging
import os

import aiohttp

from .types import EnrichedCandidate, GateResult, ModelOutput, ScoringResult, SizingDecision

logger = logging.getLogger(__name__)

TELEGRAM_SEND_URL = "https://api.telegram.org/bot{token}/sendMessage"


def _format_gates(gate_result: GateResult) -> str:
    lines = []
    for check in gate_result.checks:
        status = "✅" if check.passed else "❌"
        label = check.name.replace("_", " ")
        if check.passed:
            lines.append(f"{status} {label}")
        else:
            reason = check.reason.replace("_", " ") if check.reason else "failed"
            lines.append(f"{status} {label} ({reason})")
    return "\n".join(lines)


def _deeplink(address: str, amount: float, slippage_bps: int) -> str:
    base = "https://jup.ag/swap/SOL-{address}?inputAmount={amount}&slippageBps={slippage}"
    return base.format(address=address, amount=amount, slippage=slippage_bps)


def _build_message(candidate: EnrichedCandidate, scoring: ScoringResult, probs: ModelOutput, decision: SizingDecision, gate_result: GateResult) -> str:
    market = candidate.market
    risk = candidate.risk
    analytics = candidate.analytics

    header = f"🟢 Graduation Candidate (GS {scoring.gs:.2f}, EV {decision.ev:+.2f})"
    stats = "\n".join([
        f"MC ${(market.get('market_cap') or 0):,.0f}",
        f"LP lock {(risk.get('lock_days') or 0)}d | rep {(risk.get('locker_rep_score') or 0):.2f}",
        f"Curve {(market.get('pumpfun_curve_pct') or 0):.1f}% | Holders vel {(risk.get('holder_velocity') or 0):.2f}",
        f"Top10 {(risk.get('top10_pct') or 0)*100:.1f}% | Snipers {(risk.get('sniper_pct') or 0)*100:.1f}%",
        f"Vol15m ${(market.get('vol_15m_usd') or 0):,.0f} | Buy% {(market.get('buy_ratio_15m') or 0)*100:.1f}%",
        f"Whales15m {analytics.get('whales_inflow', 0):+.1f} SOL",
    ])
    dev_block = "\n".join([
        f"Dev rugs90d {risk.get('creator_flagged_rugs', 0)} | success10x {risk.get('creator_success_10x', 0)}",
        f"Locker {risk.get('locker_address', 'n/a')} rep {(risk.get('locker_rep_score') or 0):.2f}",
        f"Insiders {(risk.get('insider_pct') or 0)*100:.1f}% | Bundles {(analytics.get('bundle_pct') or 0)*100:.1f}%",
        f"LP adds {analytics.get('lp_adds', 0)} / removes {analytics.get('lp_removes', 0)} | Dev Δ {analytics.get('dev_liquidity_delta', 0):+.2f}",
    ])

    size_line = f"Mode {decision.mode} | size {decision.size_fraction*100:.2f}% equity"
    gates_section = _format_gates(gate_result)
    slippage_bps = 200
    buy_line = "⚡ Buy: " + " | ".join([
        f"0.1 [Jupiter]({_deeplink(candidate.address, 0.1, slippage_bps)})",
        f"0.5 [Jupiter]({_deeplink(candidate.address, 0.5, slippage_bps)})",
        f"1 [Jupiter]({_deeplink(candidate.address, 1.0, slippage_bps)})",
    ])
    links = "\n".join([
        f"🔗 [Dexscreener](https://dexscreener.com/solana/{candidate.address})",
        f"📊 [Solscan](https://solscan.io/token/{candidate.address})",
        f"🪙 [Pump](https://pump.fun/{candidate.address})",
        buy_line,
        f"🎯 [OCO Template](https://app.jup.ag/limit/{candidate.address}) | 🛑 [Panic Exit](https://jup.ag/swap/{candidate.address}-SOL?slippageBps={slippage_bps})",
    ])

    body = [
        header,
        "",
        stats,
        "",
        dev_block,
        "",
        "Gates:",
        gates_section,
        "",
        size_line,
        "",
        f"Probs loser/winner/mega: {probs.p0:.2f} / {probs.p1:.2f} / {probs.p2:.2f}",
        "",
        links,
    ]
    return "\n".join(body)


async def send_graduation_alert(candidate: EnrichedCandidate, scoring: ScoringResult, probs: ModelOutput, decision: SizingDecision, gate_result: GateResult) -> bool:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat:
        logger.warning("Telegram credentials missing; skipping alert")
        return False

    message = _build_message(candidate, scoring, probs, decision, gate_result)
    payload = {
        "chat_id": chat,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }

    async with aiohttp.ClientSession() as session:
        try:
            url = TELEGRAM_SEND_URL.format(token=token)
            async with session.post(url, json=payload, timeout=8) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    logger.error("Telegram send failed %s: %s", resp.status, text[:200])
                    return False
        except Exception as exc:
            logger.exception("Telegram send error: %s", exc)
            return False

    return True
